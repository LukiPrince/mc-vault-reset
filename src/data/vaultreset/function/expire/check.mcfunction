# Three cases. The third - loaded, but no vault there anymore - needs no line:
# the entry is simply not appended again and is gone.
$execute in $(dim) unless loaded $(x) $(y) $(z) run function vaultreset:expire/keep
$execute in $(dim) if loaded $(x) $(y) $(z) if block $(x) $(y) $(z) minecraft:vault run function vaultreset:expire/players
