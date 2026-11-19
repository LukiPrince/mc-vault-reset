# Vault Reset - initialisation. Runs on server start and on every /reload.

scoreboard objectives add vaultreset.i dummy

# Constants
scoreboard players set #5 vaultreset.i 5
scoreboard players set #20 vaultreset.i 20
scoreboard players set #60 vaultreset.i 60
scoreboard players set #3600 vaultreset.i 3600
scoreboard players set #86400 vaultreset.i 86400
scoreboard players set #max vaultreset.i 2147483647

# Create running values, never overwrite them: "add 0" creates a missing value
# as 0 and leaves an existing one untouched. With "set" every server start
# would discard all running cooldowns.
scoreboard players add #clock vaultreset.i 0
scoreboard players add #cycle vaultreset.i 0
scoreboard players add #next vaultreset.i 0

# Default configuration: 30 minutes in ticks.
execute unless data storage vaultreset:data config.cooldown run data modify storage vaultreset:data config.cooldown set value 36000
execute unless data storage vaultreset:data vaults run data modify storage vaultreset:data vaults set value []

# After a reload #next may be stale. With an empty list reset everything,
# otherwise force a scan in the next cycle - it recomputes #next anyway.
execute unless data storage vaultreset:data vaults[0] run scoreboard players set #clock vaultreset.i 0
execute unless data storage vaultreset:data vaults[0] run scoreboard players operation #next vaultreset.i = #max vaultreset.i
execute if data storage vaultreset:data vaults[0] run scoreboard players operation #next vaultreset.i = #clock vaultreset.i
