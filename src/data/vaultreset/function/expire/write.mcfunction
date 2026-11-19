# At least one player remains on cooldown: rewrite rewarded_players of the block
# from the remaining UUIDs. Single elements could not be removed - /data remove
# addresses a list of int arrays by index only, and the index is unknown without
# iterating.
$execute in $(dim) run data modify block $(x) $(y) $(z) server_data.rewarded_players set from storage vaultreset:tmp keepu
$data modify storage vaultreset:data vaults append value {x:$(x),y:$(y),z:$(z),dim:"$(dim)",players:[]}
data modify storage vaultreset:data vaults[-1].players set from storage vaultreset:tmp keepp
