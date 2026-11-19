## 1.1.0 (first public release)

Builds: `1.1.0+26.3` for Minecraft 26.3 and `1.1.0+26.2` for Minecraft 26.2. Each ships as a datapack ZIP and as Fabric, NeoForge and Quilt JARs.

- Reopen trial chamber vaults after a cooldown, default 30 minutes.
- The cooldown is set server-wide but runs per player and per vault.
- Ops get a native dialog with `/function vaultreset:menu`, or set the value with `/function vaultreset:config/set {seconds:1800}`.
- Players get a chat message when they open a vault and another when it is free again.
- 26.3: advancement updated to the new predicate format (`type` instead of `condition`, `all_of` instead of a plain list). The old format stops a 26.3 server from starting.
- The Fabric and Quilt JARs need Fabric API. NeoForge and the plain datapack need nothing else.
- The two Minecraft versions are not interchangeable. Pick the file that matches your server.
