#!/usr/bin/env python3
"""Offline lint. No framework, no server - runs with "python test_build.py".

A green result here says NOTHING about whether the pack works on a running
server. It checks structure, references and artifacts, not the semantics of the
Minecraft commands. The server procedure is described in the README.

The same file works on every branch: the Minecraft version is read from build.py
and the version-dependent checks (pack format, predicate format, version ranges)
follow it.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
LOADERS = ROOT / "loaders"

FUNC_DIR = SRC / "data" / "vaultreset" / "function"
FUNC_REF = re.compile(r"\bfunction\s+([a-z0-9_.-]+:[a-z0-9_./-]+)")
MACRO_VAR = re.compile(r"\$\(([a-z0-9_]+)\)")

# Every name a macro function may substitute. A typo such as $(dimm) would be a
# silent failure in game - here it is caught immediately.
KNOWN_VARS = {
    "x", "y", "z", "dim", "uuid", "u", "t", "su",  # registration and expiry
    "seconds", "secs", "val", "unit", "n",     # configuration
    "init", "ph",                              # slider start and dialog placeholder
}

# Not called from another function but by a human:
# /function vaultreset:config/set {seconds:1800}
MACRO_ENTRYPOINTS = {"vaultreset:config/set"}

# Deliberate exception to the macro rule: this line WRITES the placeholder that
# the dialog substitutes later on its own. It must not be a macro line, otherwise
# the function would substitute "$(secs)" already when it is called.
LITERAL_PLACEHOLDERS = {
    ("menu.mcfunction", 'data modify storage vaultreset:tmp ph set value "$(secs)"'),
}

FAILURES: list[str] = []


def check(name: str, fn) -> None:
    try:
        fn()
    except AssertionError as exc:
        FAILURES.append(f"{name}: {exc}")
        print(f"FAIL  {name}\n      {exc}")
    else:
        print(f"ok    {name}")


def _functions() -> dict[str, Path]:
    return {
        f"vaultreset:{p.relative_to(FUNC_DIR).with_suffix('').as_posix()}": p
        for p in FUNC_DIR.rglob("*.mcfunction")
    }


def test_all_json_parses() -> None:
    files = list(SRC.rglob("*.json")) + [SRC / "pack.mcmeta"] + list(LOADERS.rglob("*.json"))
    assert files, "no JSON files found"
    for f in files:
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{f.relative_to(ROOT)}: {exc}") from exc


def _mc() -> tuple[int, ...]:
    return tuple(int(x) for x in build.MC.split("."))


def _next_minor() -> str:
    major, minor = _mc()[:2]
    return f"{major}.{minor + 1}"


def test_pack_format() -> None:
    pack = json.loads((SRC / "pack.mcmeta").read_text(encoding="utf-8"))["pack"]
    if _mc() >= (26, 3):
        # 26.3 = format 121.0. An integer max_format covers every minor version of
        # 121 (hotfixes) but not 26.4.
        assert pack["min_format"] == [121, 0], pack["min_format"]
        assert pack["max_format"] == 121, pack["max_format"]
    else:
        # 26.2 = format 107.1
        assert pack["min_format"] == [107, 0], pack["min_format"]
        assert pack["max_format"] == [107, 1], pack["max_format"]


def test_advancement_predicates() -> None:
    """From 26.3 on, `location` is a single predicate: a list is no longer
    shorthand for all_of, and the type key is `type` instead of `condition`. The
    wrong format does not fail silently but keeps the whole server from starting
    ("Failed to load registries"). Up to 26.2 the old format is required."""
    adv = json.loads((SRC / "data/vaultreset/advancement/unlocked.json").read_text(encoding="utf-8"))
    new_format = _mc() >= (26, 3)

    def walk(node, path):
        if isinstance(node, dict):
            if new_format:
                assert "condition" not in node, f"{path}: 'condition' instead of 'type' (format up to 26.2)"
            else:
                assert "type" not in node, f"{path}: 'type' instead of 'condition' (format from 26.3)"
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    for name, crit in adv["criteria"].items():
        loc = crit["conditions"]["location"]
        if new_format:
            assert isinstance(loc, dict), f"{name}: location is a list (format up to 26.2)"
            assert loc.get("type") == "minecraft:all_of", f"{name}: location.type = {loc.get('type')}"
            assert all("type" in t for t in loc["terms"]), f"{name}: term without type"
        else:
            assert isinstance(loc, list), f"{name}: location is not a list (format from 26.3)"
            assert all("condition" in t for t in loc), f"{name}: term without condition"
        walk(crit, name)


def test_function_refs_resolve() -> None:
    funcs = _functions()
    refs = set()
    for p in FUNC_DIR.rglob("*.mcfunction"):
        refs |= {(m, p) for m in FUNC_REF.findall(p.read_text(encoding="utf-8"))}
    adv = json.loads((SRC / "data/vaultreset/advancement/unlocked.json").read_text(encoding="utf-8"))
    refs.add((adv["rewards"]["function"], Path("unlocked.json")))
    for tag in (SRC / "data/minecraft/tags/function").glob("*.json"):
        for v in json.loads(tag.read_text(encoding="utf-8"))["values"]:
            refs.add((v, tag))
    for ref, src in sorted(refs):
        assert ref in funcs, f"{ref} referenced in {Path(src).name}, but no such file"


def test_every_function_reachable() -> None:
    funcs = _functions()
    reached = {"vaultreset:load", "vaultreset:tick"}
    for p in FUNC_DIR.rglob("*.mcfunction"):
        reached |= set(FUNC_REF.findall(p.read_text(encoding="utf-8")))
    adv = json.loads((SRC / "data/vaultreset/advancement/unlocked.json").read_text(encoding="utf-8"))
    reached.add(adv["rewards"]["function"])
    orphans = sorted(set(funcs) - reached)
    assert not orphans, f"never called: {orphans}"


def test_macro_lines_marked() -> None:
    for p in FUNC_DIR.rglob("*.mcfunction"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("#") or "$(" not in line:
                continue
            if (p.name, line.strip()) in LITERAL_PLACEHOLDERS:
                continue
            assert line.startswith("$"), f"{p.name}:{i} uses $(...) but does not start with $"


def test_macro_vars_known() -> None:
    for p in FUNC_DIR.rglob("*.mcfunction"):
        for var in MACRO_VAR.findall(p.read_text(encoding="utf-8")):
            assert var in KNOWN_VARS, f"{p.name}: unknown macro variable $({var})"


def test_macro_functions_called_with_args() -> None:
    funcs = _functions()
    # A macro function is one with a line starting with $ - not merely one that
    # has $( somewhere in its text.
    macros = {
        fid
        for fid, p in funcs.items()
        if any(
            line.startswith("$") and MACRO_VAR.search(line)
            for line in p.read_text(encoding="utf-8").splitlines()
        )
    }
    callers = "\n".join(
        p.read_text(encoding="utf-8") for p in FUNC_DIR.rglob("*.mcfunction")
    )
    for fid in sorted(macros - MACRO_ENTRYPOINTS):
        assert re.search(rf"function\s+{re.escape(fid)}\s+with\s+", callers), (
            f"{fid} is a macro function but is never called with 'with'"
        )


def test_version_consistent() -> None:
    fab = json.loads((LOADERS / "fabric/fabric.mod.json").read_text(encoding="utf-8"))
    quilt = json.loads((LOADERS / "quilt/quilt.mod.json").read_text(encoding="utf-8"))
    toml = (LOADERS / "neoforge/META-INF/neoforge.mods.toml").read_text(encoding="utf-8")
    full = f"{build.VERSION}+{build.MC}"
    assert build.FULL_VERSION == full, build.FULL_VERSION
    assert fab["version"] == full, fab["version"]
    assert quilt["quilt_loader"]["version"] == full, quilt["quilt_loader"]["version"]
    assert f'version = "{full}"' in toml, "version missing in neoforge.mods.toml"


def test_mc_ranges() -> None:
    """Every loader pins Minecraft to exactly the version in build.py."""
    nxt = _next_minor()
    fab = json.loads((LOADERS / "fabric/fabric.mod.json").read_text(encoding="utf-8"))
    quilt = json.loads((LOADERS / "quilt/quilt.mod.json").read_text(encoding="utf-8"))
    toml = (LOADERS / "neoforge/META-INF/neoforge.mods.toml").read_text(encoding="utf-8")
    assert fab["depends"]["minecraft"] == f">={build.MC} <{nxt}", fab["depends"]["minecraft"]
    qdep = next(d for d in quilt["quilt_loader"]["depends"] if d["id"] == "minecraft")
    # The trailing "-" makes the bounds cover pre-releases of the boundary version.
    assert qdep["versions"] == {"all": [f">={build.MC}-", f"<{nxt}-"]}, qdep["versions"]
    assert f'versionRange = "[{build.MC},{nxt})"' in toml, "NeoForge range does not match MC"


def test_loader_dependencies() -> None:
    """Fabric and Quilt ignore data/ in a code-free JAR without Fabric API, silently.
    NeoForge needs no modLoader entry; lowcodefml is deprecated."""
    fab = json.loads((LOADERS / "fabric/fabric.mod.json").read_text(encoding="utf-8"))
    quilt = json.loads((LOADERS / "quilt/quilt.mod.json").read_text(encoding="utf-8"))
    toml = (LOADERS / "neoforge/META-INF/neoforge.mods.toml").read_text(encoding="utf-8")
    assert "fabric-api" in fab["depends"], "fabric.mod.json does not depend on fabric-api"
    ids = [d["id"] if isinstance(d, dict) else d for d in quilt["quilt_loader"]["depends"]]
    assert "fabric-api" in ids, "quilt.mod.json does not depend on fabric-api"
    assert not re.search(r"^\s*modLoader\s*=", toml, re.M), "neoforge.mods.toml sets modLoader"


def test_artifacts() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        paths = build.build(outdir=Path(tmp))
        assert len(paths) == 4, [p.name for p in paths]
        expect = {
            "datapack": None,
            "fabric": "fabric.mod.json",
            "neoforge": "META-INF/neoforge.mods.toml",
            "quilt": "quilt.mod.json",
        }
        for path in paths:
            kind = path.stem.rsplit("-", 1)[-1]
            with zipfile.ZipFile(path) as zf:
                names = set(zf.namelist())
            assert "pack.mcmeta" in names, f"{path.name} without pack.mcmeta"
            assert any(n.startswith("data/") for n in names), f"{path.name} without data/"
            meta = expect[kind]
            if meta:
                assert meta in names, f"{path.name} without {meta}"
            else:
                assert not any(n.endswith(".mod.json") for n in names), "ZIP contains loader metadata"


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            check(name, fn)
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
