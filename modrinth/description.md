Vault Reset lets players open a trial chamber vault again after a cooldown. Normally a vault is locked for you for good once you have used it. With this pack the lock lifts after a time the server sets, by default 30 minutes.

It is a datapack with no Java code. You can run it as a plain datapack, or as a mod JAR on Fabric, NeoForge or Quilt (the JARs only contain the same data files).

<!-- screenshot: scene, player at a vault in a trial chamber -->

## What it does

**For players.** Put a trial key into a vault as usual. You get a chat message like "Vault at x y z, open again for you in 15 s". When the time is up you get a second one: "Vault at x y z is open again". Then the vault gives loot again.

The cooldown is tracked per player and per vault. If player A empties a vault, it stays open for player B. Each vault also counts separately, so using one does not lock the others.

**For admins.** The cooldown length is one setting for the whole server. Ops can change it with a dialog window or a command:

```
/function vaultreset:menu
/function vaultreset:config/set {seconds:1800}
```

The first command opens a native dialog (not a chest GUI or chat menu). It shows the current value, a slider from 5 seconds to 2 hours in 5-second steps, six presets, and how many vaults are on cooldown right now. Escape closes it. `/function` needs permission level 2, and the dialog buttons run with the rights of whoever clicks, so non-ops cannot use the menu.

The command accepts 5 seconds to 30 days and rounds to 5-second steps.

<!-- screenshot: dialog menu -->

<!-- screenshot: chat messages after opening a vault -->

## How it works

When a player uses a trial key on a vault, the pack finds the block that was used and remembers it, together with the players who have already used it. Every 100 ticks it checks whether any cooldown has run out. When one has, that player is removed from the vault's list of rewarded players, so the vault accepts their key again. Once nobody is waiting on a vault, its entry is dropped. There are no marker entities running in the background.

Vaults that players used before you installed the pack are picked up the first time someone uses them, so they are not stuck.

## Installation

| Platform | File | Put it in |
|---|---|---|
| Vanilla or Paper | `vault-reset-1.1.0+26.3-datapack.zip` | `<world>/datapacks/` |
| Fabric | `vault-reset-1.1.0+26.3-fabric.jar` | `mods/`, together with [Fabric API](https://modrinth.com/mod/fabric-api) |
| NeoForge | `vault-reset-1.1.0+26.3-neoforge.jar` | `mods/` |
| Quilt | `vault-reset-1.1.0+26.3-quilt.jar` | `mods/`, together with [Fabric API](https://modrinth.com/mod/fabric-api) |

For Minecraft 26.2, use the files with `+26.2` in the name instead. Run `/reload` or restart the server after adding the file.

The JARs contain no code, only the same data files as the ZIP. NeoForge loads them on its own. Fabric and Quilt need Fabric API for that, and the JARs declare it as a dependency, so the loader tells you if it is missing. On Quilt, use the regular Fabric API.

To update, remove the old file and add the new one. The configuration and running cooldowns are stored in `storage vaultreset:data` and are kept.

## Compatibility

| Pack version | Minecraft | Datapack format |
|---|---|---|
| 1.1.0+26.3 | 26.3 | 121 |
| 1.1.0+26.2 | 26.2 | 107.1 |

The two builds are not interchangeable. 26.3 changed the advancement format, and the 26.2 build makes a 26.3 server fail to start. The 26.3 build is not meant for 26.2.

What has been tested: all eight files (ZIP, Fabric, NeoForge and Quilt for both Minecraft versions) on their own test servers, covering registration, the per-player expiry and a clean server log. Earlier builds of the datapack were also played in the game on 26.3 and 26.2: key in vault, chat messages and menu all worked.

## Limitations

- The cooldown pauses while the server is offline. A datapack cannot read a real-time clock.
- Resolution is 5 seconds.
- If a vault is in an unloaded chunk when its time is up, the reset waits for the next cycle, and keeps waiting until the chunk loads.
- Vaults in modded dimensions are not tracked. Only the Overworld, Nether and End are recognised, because vanilla offers no way to read the current dimension as a string. A vault in an unknown dimension is ignored on purpose, rather than risking writes to the wrong world.
- There is no live countdown at the block. Players hear the duration when they open the vault and get a message when it is free again, nothing in between. A display above the vault would need one text display entity per cooldown, which this pack avoids.
- If a player is offline when their cooldown ends, they miss the chat message. The vault is still released.
- Not tested yet: two real players at the same time (the separation is checked on the data level only), and long-term behaviour with many cooldowns running at once.

## Links

- Source code: https://github.com/LukiPrince/mc-vault-reset
- Bug reports and requests: https://github.com/LukiPrince/mc-vault-reset/issues
- License: MIT
