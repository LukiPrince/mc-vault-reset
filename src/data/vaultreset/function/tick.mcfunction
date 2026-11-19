# Runs every tick. Everything else costs compute time only every 100 ticks (5 s).
scoreboard players add #cycle vaultreset.i 1
execute if score #cycle vaultreset.i matches 100.. run function vaultreset:cycle
