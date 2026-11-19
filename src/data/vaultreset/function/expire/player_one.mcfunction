data modify storage vaultreset:tmp p set from storage vaultreset:tmp pw[0]
data remove storage vaultreset:tmp pw[0]
execute store result score #t vaultreset.i run data get storage vaultreset:tmp p.t

# Expired entries are simply not carried over.
execute if score #t vaultreset.i > #clock vaultreset.i run function vaultreset:expire/player_keep

# ... but the player is told about it, if online.
data modify storage vaultreset:cur v.u set from storage vaultreset:tmp p.u
execute unless score #t vaultreset.i > #clock vaultreset.i run function vaultreset:expire/notify with storage vaultreset:cur v
