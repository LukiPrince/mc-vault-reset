# Nobody on cooldown anymore: release the block and drop the entry.
$execute in $(dim) run data modify block $(x) $(y) $(z) server_data.rewarded_players set value []
