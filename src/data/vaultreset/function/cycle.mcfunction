# One cycle every 100 ticks. The normal case costs exactly this one comparison.
scoreboard players set #cycle vaultreset.i 0
scoreboard players add #clock vaultreset.i 100
execute if score #clock vaultreset.i >= #next vaultreset.i run function vaultreset:expire/scan
