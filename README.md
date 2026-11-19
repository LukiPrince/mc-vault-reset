# Vault Reset

Lets players reopen trial chamber vaults after a cooldown. The configured value applies
**server-wide**, but the cooldown itself runs **separately per player and vault**: the fact that
player A emptied a vault does not lock it for player B.

Pure datapack, no Java code. This branch (`main`) targets **Minecraft 26.3** (datapack format 121).

The predecessor `ReOpenable Vaults DP` (last release for 1.21.9 to 1.21.11) no longer loads on
current datapack formats, and its `CC-BY-NC-ND` license rules out a fork, so this is a fresh
implementation.

| Version | Minecraft | Datapack format | Branch |
|---|---|---|---|
| 1.1.0+26.3 | 26.3 | 121 | `main` |
| 1.1.0+26.2 | 26.2 | 107.1 | `mc/26.2` |

The versions are not interchangeable: 26.3 changed the advancement format (see
[Changes for 26.3](#changes-for-263)). The 26.2 build does not let a 26.3 server start at all, and
the 26.3 build is not meant for 26.2.

Branches: `main` always carries the newest supported Minecraft version. Every older version that is
incompatible with it gets a maintenance branch named `mc/<version>`, for example `mc/26.2`. Version
numbers follow `x.y.z+<minecraft version>`.

Tested on real servers, 26.2 in-game and 26.3 in-game plus via RCON. See [Test record](#test-record)
for what is verified and what is not.

## Installation

| Target | File | Location |
|---|---|---|
| Vanilla / Paper | `vault-reset-1.1.0+26.3-datapack.zip` | `<world>/datapacks/` |
| Fabric | `vault-reset-1.1.0+26.3-fabric.jar` | `mods/`, together with [Fabric API](https://modrinth.com/mod/fabric-api) |
| NeoForge | `vault-reset-1.1.0+26.3-neoforge.jar` | `mods/` |
| Quilt | `vault-reset-1.1.0+26.3-quilt.jar` | `mods/`, together with [Fabric API](https://modrinth.com/mod/fabric-api) |

Updating: remove the old ZIP from `datapacks/` and drop the new one in. The server then reports a
missing data pack for the old file and loads the new one on its own. Configuration and running
cooldowns live in `storage vaultreset:data` and are kept.

The JARs contain no Java code. NeoForge mounts the `data/` directory of a mod JAR as a datapack
on its own. Fabric and Quilt need **Fabric API** for that: without it the JAR is ignored
silently and every `/function vaultreset:...` is unknown. Both manifests therefore declare
`fabric-api` as a dependency, so the loader stops with a clear message instead. On Quilt, use
the regular Fabric API; there is no Quilted Fabric API for 26.x.

## Usage

```
/function vaultreset:menu                             GUI window (ops only)
/function vaultreset:config/set {seconds:1800}        set the cooldown directly
```

Default is 30 minutes. The range is 5 seconds to 30 days, rounded down to steps of 5 seconds.

The player gets two chat messages: when opening, "Vault at x y z - open again for you in 15 s", and
on expiry "Vault at x y z is open again". The player is addressed via `@a[nbt={UUID:...}]`. If the
player is offline, the second message is skipped, but the vault block is released regardless.

### The menu

`/function vaultreset:menu` opens a **native dialog window** (registry `minecraft:dialog`, since
1.21.6): no item in the inventory, no chat history, Escape closes it. It shows the current value, a
slider from 5 s to 2 h in 5-second steps, six presets and the number of vaults currently on
cooldown.

Permissions are handled by vanilla: `/function` requires permission level 2, and the dialog buttons
run with the permissions of whoever clicks. Non-ops therefore reach neither the menu nor the
buttons. A custom trigger or admin tag is not needed.

Two quirks that would otherwise look odd when reading the code:

- The dialog is passed **inline** to `/dialog show` instead of as a registry file. Registry dialogs
  are static; the current value and the slider start could not be inserted there.
- Dialog templates use the **same** `$(key)` syntax as macro functions. For the slider placeholder
  to survive the macro step, `menu.mcfunction` stores it as a string on a deliberately non-macro
  line, and `menu/show.mcfunction` inserts it as `$(ph)`. `test_build.py` knows this one exception
  by name.

## How it works

1. When a player puts a trial key into a vault, the advancement criterion
   `minecraft:item_used_on_block` fires, the same one vanilla uses for *Under Lock and Key*.
2. A raycast from the eyes (30 steps of 0.2 blocks) finds the block. `align xyz` plus a short-lived
   marker yield the block position as integers, also for negative coordinates.
3. The vault is stored in `storage vaultreset:data` as `{x, y, z, dim, players:[{u, t}]}`. On first
   contact, players already listed in the block are carried over, so vaults used before installation
   do not stay burned.
4. Every 100 ticks: one score comparison. Only when the smallest expiry value is reached does the
   scan run over the list and rewrite `server_data.rewarded_players` from the remaining UUIDs.
5. When nobody is on cooldown anymore, the entry is dropped. When the list is empty, the counter is
   reset to zero.

No marker entities in continuous operation, no entity budget, nothing a `/kill @e` could wipe out.

## Limits

- **The cooldown pauses while the server is off.** Vanilla datapacks have no access to a real-time
  clock; anything else would be a lie.
- Resolution is 5 seconds.
- If the vault is in an unloaded chunk, the reset is postponed to the next cycle, as often as
  needed, until the chunk loads.
- Vaults in modded dimensions are **not** tracked. Vanilla has no way to read the current dimension
  as a string; Overworld, Nether and End are recognised. An unknown dimension deliberately leads to
  no registration at all instead of a write to the wrong world.
- The `#clock` counter is an `int` and would overflow after about 3.4 years of continuous server
  uptime. It is reset whenever the vault list is empty, which happens constantly in normal
  operation.
- There is no running countdown display at the block. The player learns the duration when opening
  and the release on expiry; in between they cannot ask. A display above the vault would need one
  `text_display` entity per cooldown plus an update every cycle: exactly the entity budget this
  pack deliberately avoids.

## Changes for 26.3

Only the advancement `vaultreset:unlocked` was affected. Two changes in 26.3
([Java Edition 26.3](https://minecraft.wiki/w/Java_Edition_26.3), sections "Predicate" and
"Advancement definition > Triggers"):

- The type key of predicates is `type` instead of `condition`.
- A list is no longer shorthand for `minecraft:all_of`. The `location` field of
  `item_used_on_block` takes a single predicate (inline or as an ID); several conditions go into
  `{"type": "minecraft:all_of", "terms": [...]}`, exactly how vanilla 26.3 writes its own
  advancement *Revaulting*.

With the old format, 26.3 aborts on startup: `Failed to parse vaultreset:unlocked ... Not a JSON
object`, followed by `Failed to load datapacks, can't proceed with server load`. So it does not
fail silently but takes the whole server down. `test_build.py` therefore checks the format.

Functions, macros, dialog, `tellraw` and the vault block data (`server_data.rewarded_players`)
needed no change.

## Building

```bash
python build.py          # -> dist/, four artifacts
python test_build.py     # offline lint
```

Python 3 standard library only. No Gradle, no JDK, no network access.

`test_build.py` checks: all JSON parses, every referenced `function ns:path` exists, no function is
orphaned, every line with `$(...)` starts with `$`, every macro variable is a known one, every macro
function is called with `with`, versions and Minecraft ranges agree across all loader manifests,
the pack format and advancement predicate format match the Minecraft version in `build.py`, and
every artifact contains what it should. The same file works on all branches.

## Test record

### All artifacts, 1.1.0+26.3 and 1.1.0+26.2 (2026-11-19)

Local throwaway servers per Minecraft version, flat world, no players, driven via RCON.
Each artifact ran through the same 15 checks on its own server:

| Artifact | 26.3 | 26.2 |
|---|---|---|
| Datapack ZIP on vanilla | pass | pass |
| Fabric JAR + Fabric API | pass (Loader 0.20.1, API 0.166.2) | pass (API 0.161.0) |
| NeoForge JAR | pass (26.3.0.113) | pass (26.2.0.95) |
| Quilt JAR + Fabric API | pass (Loader 0.30.2) | pass |

The checks: pack enabled; `config/set {seconds:10}` stores `200`; three vaults registered via
`register/found`, one of them pre-filled with a foreign UUID; a second player upserted with a
100 s cooldown; after expiry the single-player vault is cleared, the shared one keeps only the
second player, the pre-filled one is cleared and storage holds just the remaining vault;
`#clock` advances; `latest.log` has no warnings or errors from the pack.

On vanilla, every macro that builds chat or dialog text was also called with real values
(`menu/show`, `register/say`, `expire/notify`, `config/say`, `menu`): all instantiate and parse.
Not covered without a player: the advancement trigger, the raycast, and how dialog and chat
text render in a client.

Without Fabric API, the Fabric and Quilt JARs were ignored silently (see Installation). With
the old `modLoader = "lowcodefml"`, NeoForge logged a deprecation warning; the manifest no
longer sets it.

### Verified on 26.3 (1.1.0, 2026-11-14)

Fabric server 26.3 with a copy of a real world, no players, via RCON. The **datapack ZIP** was
loaded; the JARs were tested later, see above.

| Behaviour | How checked |
|---|---|
| Pack loads, no load errors, update from 1.0.0 keeps configuration and list | server start, log, `/datapack list enabled`, storage before/after |
| Setting the cooldown, rounding to ticks | `config/set {seconds:10}` gives `200`, `{seconds:1800}` gives `36000` |
| Dialog macro instantiates on 26.3 | `function vaultreset:menu/show {...}` with real values: runs; with a broken `init` as control: "Failed to instantiate" |
| `tellraw` macros (`register/say`, `expire/notify`, `config/say`) parse | line with substituted values directly via RCON, selector without match gives "No player was found" |
| Vault block data unchanged (`server_data.rewarded_players`) | `data get block` on a freshly placed vault |
| Upsert and takeover of already present `rewarded_players` | `register/upsert` with a pre-filled block |
| Expiry **per player**: expired UUID removed, running one stays in block and list | two UUIDs with 10 s and 100 s |
| Last entry expires: block cleared, entry gone | second vault, both UUIDs due |

**In-game on 26.3 (2026-11-14):** a trial key was put into a vault. Advancement trigger, raycast,
registration and chat message work, as does the menu.

### Verified on 26.2 (1.0.0)

| Behaviour | How checked |
|---|---|
| Pack loads, `load` initialises, no load errors | server start + `/datapack list enabled` |
| All commands parse, including dialog and `tellraw` macros | called every function, log without errors |
| Setting the cooldown, clamping and 5 s rounding | `config/set {seconds:10}` gives `200` ticks |
| Registration: advancement trigger, raycast, entry with UUID | vault opened in game |
| Expiry **per player**: expired UUID removed, running one stays | two UUIDs inserted, one due |
| Last entry expires: block cleared, entry gone, `clock` reset | continuation of the same test |
| Chunk not loaded: entry stays, retry next cycle | test without player, without `forceload` |
| Takeover of already present `rewarded_players` | `register/upsert` with a pre-filled block |
| Dialog opens, presets and slider set the value | clicked and dragged in game |
| Chat messages reach the right player | delivered via the real UUID |

### Open

- **Two simultaneous players.** The separation is verified at data level (two UUIDs, separate
  expiry values) but has never been played with two real accounts.
- **Modded dimensions**: deliberately not tracked, see Limits.
- **Long-term behaviour**, for example many cooldowns running at the same time.

### Reproduction procedure

```
/reload
# 1. Does the pack load at all?
/datapack list

# 2. Configuration
/function vaultreset:config/set {seconds:10}
/data get storage vaultreset:data config.cooldown      -> 200

# 3. Menu
/function vaultreset:menu                              -> dialog window with slider and presets

# 4. Vault
/setblock ~ ~1 ~ minecraft:vault
/give @s minecraft:trial_key 2
# open the vault, then:
/data get storage vaultreset:data vaults               -> one entry with your own UUID
/data get block ~ ~1 ~ server_data.rewarded_players    -> your UUID inside

# 5. After 10 seconds
/data get block ~ ~1 ~ server_data.rewarded_players    -> empty
/data get storage vaultreset:data vaults               -> empty
# open the vault again -> must give loot again
```

Without players the chunks stay unloaded, and the postponement path applies instead of the expiry.
For tests via RCON, set `forceload add 0 0` and `pause-when-empty-seconds=0` in
`server.properties`, otherwise the server pauses with an empty player slot and the tick does not
run.

## License

MIT, see [LICENSE](LICENSE).
