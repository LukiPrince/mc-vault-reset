# Feedback to the player who just opened the vault - addressed by UUID,
# because @s here would be the marker that was already removed.
$tellraw @a[nbt={UUID:$(uuid)}] [{"text":"[Vault Reset] ","color":"dark_aqua"},{"text":"Vault at ","color":"gray"},{"text":"$(x) $(y) $(z)","color":"white"},{"text":" - open again for you in ","color":"gray"},{"text":"$(val) $(unit)","color":"dark_green"},{"text":".","color":"gray"}]
