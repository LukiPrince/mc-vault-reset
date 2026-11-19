execute if block ~ ~ ~ minecraft:vault run function vaultreset:register/found
execute unless block ~ ~ ~ minecraft:vault run scoreboard players remove #ray vaultreset.i 1
execute unless block ~ ~ ~ minecraft:vault if score #ray vaultreset.i matches 1.. positioned ^ ^ ^0.2 run function vaultreset:register/ray
