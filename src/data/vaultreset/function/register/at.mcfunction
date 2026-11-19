# @s = short-lived marker on the block corner of the vault that was hit.
execute store result score #x vaultreset.i run data get entity @s Pos[0]
execute store result score #y vaultreset.i run data get entity @s Pos[1]
execute store result score #z vaultreset.i run data get entity @s Pos[2]

# Vanilla has no way to read the current dimension as a string.
# Empty string as default: an unknown (modded) dimension then leads to no
# registration at all instead of a write access to the wrong world.
data modify storage vaultreset:tmp dim set value ""
execute if dimension minecraft:overworld run data modify storage vaultreset:tmp dim set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage vaultreset:tmp dim set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage vaultreset:tmp dim set value "minecraft:the_end"
kill @s

execute store result storage vaultreset:tmp x int 1 run scoreboard players get #x vaultreset.i
execute store result storage vaultreset:tmp y int 1 run scoreboard players get #y vaultreset.i
execute store result storage vaultreset:tmp z int 1 run scoreboard players get #z vaultreset.i

execute store result score #t vaultreset.i run data get storage vaultreset:data config.cooldown
scoreboard players operation #t vaultreset.i += #clock vaultreset.i
execute store result storage vaultreset:tmp t int 1 run scoreboard players get #t vaultreset.i

# Readable duration for the feedback to the player.
execute store result score #cd vaultreset.i run data get storage vaultreset:data config.cooldown
scoreboard players operation #cd vaultreset.i /= #20 vaultreset.i
function vaultreset:util/fmt

execute unless data storage vaultreset:tmp {dim:""} run function vaultreset:register/upsert with storage vaultreset:tmp
