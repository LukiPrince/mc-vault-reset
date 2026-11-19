# "align xyz" rounds down correctly, also for negative coordinates - unlike
# "store result score", which truncates toward zero and would shift the block by
# one. The marker then sits exactly on the block corner, so its Pos is integral
# and can be read without loss.
execute align xyz summon minecraft:marker run function vaultreset:register/at
