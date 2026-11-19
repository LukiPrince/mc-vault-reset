# Changelog

Versions follow `x.y.z+<minecraft version>`. The branch `main` carries the newest supported
Minecraft version, older ones live on `mc/<version>` branches.

## 1.1.0+26.3

First public release for Minecraft 26.3 (datapack format 121).

- All in-game texts (chat messages, menu dialog) are now in English.
- New version scheme `x.y.z+<minecraft version>`, also used in the file names.
- The Quilt manifest now has an upper bound for Minecraft (`<26.4`), like Fabric and NeoForge.
- The Fabric and Quilt JARs now declare Fabric API as a dependency. Without it, both loaders
  ignored the JAR silently; now they stop with a message that names the missing mod.
- The NeoForge manifest no longer sets `modLoader = "lowcodefml"`, which NeoForge reports as
  deprecated. The JAR loads the same way without it.
- Repository, comments and documentation translated to English; MIT license added.
- `test_build.py` checks pack format, predicate format and version ranges against the Minecraft
  version configured in `build.py`.

## 1.1.0+26.2

First public release for Minecraft 26.2 (datapack format 107.1), branch `mc/26.2`. Same changes as
1.1.0+26.3, with the pre-26.3 advancement predicate format.

## Earlier private releases

1.0.0 (Minecraft 26.2) and 1.1.0 (Minecraft 26.3) were private releases with German in-game texts.
