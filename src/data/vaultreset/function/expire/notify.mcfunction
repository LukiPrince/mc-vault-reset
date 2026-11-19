# Matches nobody if the player is offline - that is fine, the block was
# released anyway.
$tellraw @a[nbt={UUID:$(u)}] [{"text":"[Vault Reset] ","color":"dark_aqua"},{"text":"Vault at ","color":"gray"},{"text":"$(x) $(y) $(z)","color":"white"},{"text":" is open again.","color":"dark_green"}]
