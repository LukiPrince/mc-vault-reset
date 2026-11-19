#!/usr/bin/env python3
"""Builds four artifacts from one source: a vanilla datapack ZIP plus one
code-free mod JAR each for Fabric, NeoForge and Quilt.

The JARs contain no Java code - hence no Gradle and no JDK. NeoForge mounts the
data/ directory of a mod JAR as a datapack on its own; Fabric and Quilt need
Fabric API for that, which both manifests declare as a dependency.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
LOADERS = ROOT / "loaders"
VERSION = "1.1.0"
MC = "26.3"  # Minecraft version this branch targets
FULL_VERSION = f"{VERSION}+{MC}"  # scheme used in file names and manifests

# name -> (loader directory under loaders/ or None, extension)
TARGETS = {
    "datapack": (None, ".zip"),
    "fabric": ("fabric", ".jar"),
    "neoforge": ("neoforge", ".jar"),
    "quilt": ("quilt", ".jar"),
}

# Fixed timestamps so that two builds of the same source are byte-identical.
FIXED_TIME = (2026, 8, 1, 0, 0, 0)


def _files(base: Path) -> list[Path]:
    return sorted(p for p in base.rglob("*") if p.is_file())


def _add(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, path.read_bytes())


def build(version: str = FULL_VERSION, outdir: Path | None = None) -> list[Path]:
    """Builds all artifacts and returns their paths."""
    outdir = outdir or ROOT / "dist"
    outdir.mkdir(parents=True, exist_ok=True)

    built = []
    for name, (loader, ext) in TARGETS.items():
        out = outdir / f"vault-reset-{version}-{name}{ext}"
        with zipfile.ZipFile(out, "w") as zf:
            for f in _files(SRC):
                _add(zf, f, f.relative_to(SRC).as_posix())
            if loader:
                ldir = LOADERS / loader
                for f in _files(ldir):
                    _add(zf, f, f.relative_to(ldir).as_posix())
        built.append(out)
    return built


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", default=FULL_VERSION)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    for path in build(args.version, args.out):
        print(f"{path.name:44} {path.stat().st_size:>8} B")


if __name__ == "__main__":
    main()
