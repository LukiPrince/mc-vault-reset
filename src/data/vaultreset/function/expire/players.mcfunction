data modify storage vaultreset:tmp pw set from storage vaultreset:tmp cur.players
data modify storage vaultreset:tmp keepp set value []
data modify storage vaultreset:tmp keepu set value []
function vaultreset:expire/player_next

execute if data storage vaultreset:tmp keepp[0] run function vaultreset:expire/write with storage vaultreset:cur v
execute unless data storage vaultreset:tmp keepp[0] run function vaultreset:expire/clear with storage vaultreset:cur v
