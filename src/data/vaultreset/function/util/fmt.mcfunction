# Expects #cd in seconds. Sets #val and storage vaultreset:tmp val/unit to the
# largest unit that divides without remainder - otherwise 90 minutes would read
# "1 h". The later line wins, hence ascending order.
scoreboard players operation #val vaultreset.i = #cd vaultreset.i
data modify storage vaultreset:tmp unit set value "s"
scoreboard players operation #m vaultreset.i = #cd vaultreset.i
scoreboard players operation #m vaultreset.i %= #60 vaultreset.i
execute if score #cd vaultreset.i matches 60.. if score #m vaultreset.i matches 0 run function vaultreset:util/unit_min
scoreboard players operation #m vaultreset.i = #cd vaultreset.i
scoreboard players operation #m vaultreset.i %= #3600 vaultreset.i
execute if score #cd vaultreset.i matches 3600.. if score #m vaultreset.i matches 0 run function vaultreset:util/unit_h
scoreboard players operation #m vaultreset.i = #cd vaultreset.i
scoreboard players operation #m vaultreset.i %= #86400 vaultreset.i
execute if score #cd vaultreset.i matches 86400.. if score #m vaultreset.i matches 0 run function vaultreset:util/unit_d
execute store result storage vaultreset:tmp val int 1 run scoreboard players get #val vaultreset.i
