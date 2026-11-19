# /function vaultreset:config/set {seconds:1800}
$scoreboard players set #cfg vaultreset.i $(seconds)
function vaultreset:config/apply
execute store result storage vaultreset:tmp secs int 1 run scoreboard players get #cfg vaultreset.i
execute if entity @s run function vaultreset:config/say with storage vaultreset:tmp
