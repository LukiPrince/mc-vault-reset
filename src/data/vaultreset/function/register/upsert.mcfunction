# NBT paths address list elements by compound filter. So neither finding the
# vault nor replacing the player entry needs a loop - "remove" followed by
# "append" is the upsert.
$execute unless data storage vaultreset:data vaults[{x:$(x),y:$(y),z:$(z),dim:"$(dim)"}] run function vaultreset:register/create with storage vaultreset:tmp
$execute if data storage vaultreset:data vaults[{x:$(x),y:$(y),z:$(z),dim:"$(dim)"}].players[{u:$(uuid)}] run data remove storage vaultreset:data vaults[{x:$(x),y:$(y),z:$(z),dim:"$(dim)"}].players[{u:$(uuid)}]
$data modify storage vaultreset:data vaults[{x:$(x),y:$(y),z:$(z),dim:"$(dim)"}].players append value {u:$(uuid),t:$(t)}
execute if score #t vaultreset.i < #next vaultreset.i run scoreboard players operation #next vaultreset.i = #t vaultreset.i
function vaultreset:register/say with storage vaultreset:tmp
