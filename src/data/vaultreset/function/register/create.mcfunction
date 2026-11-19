# New vault. Players already listed in the block are carried over, so vaults
# used before installation do not stay burned forever.
$data modify storage vaultreset:data vaults append value {x:$(x),y:$(y),z:$(z),dim:"$(dim)",players:[]}
data modify storage vaultreset:tmp sw set value []
$execute in $(dim) if data block $(x) $(y) $(z) server_data.rewarded_players[0] run data modify storage vaultreset:tmp sw set from block $(x) $(y) $(z) server_data.rewarded_players
execute if data storage vaultreset:tmp sw[0] run function vaultreset:register/seed_next
