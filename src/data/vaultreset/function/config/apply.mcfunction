# Expects the requested value in seconds in #cfg and writes it, clamped and
# rounded down to 5 s, as ticks to storage. Afterwards #cfg holds the effective
# value in seconds - callers report it back.

# Clamp: 5 s to 30 days.
execute if score #cfg vaultreset.i matches ..4 run scoreboard players set #cfg vaultreset.i 5
execute if score #cfg vaultreset.i matches 2592001.. run scoreboard players set #cfg vaultreset.i 2592000

# Round down to 5 s - the pack cannot resolve anything finer than its tick cycle.
scoreboard players operation #cfg vaultreset.i /= #5 vaultreset.i
scoreboard players operation #cfg vaultreset.i *= #5 vaultreset.i

scoreboard players operation #cfgt vaultreset.i = #cfg vaultreset.i
scoreboard players operation #cfgt vaultreset.i *= #20 vaultreset.i
execute store result storage vaultreset:data config.cooldown int 1 run scoreboard players get #cfgt vaultreset.i
