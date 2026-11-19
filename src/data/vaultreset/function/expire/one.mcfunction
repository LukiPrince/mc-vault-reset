data modify storage vaultreset:tmp cur set from storage vaultreset:tmp work[0]
data remove storage vaultreset:tmp work[0]

# Argument compound for the macros: only x/y/z/dim, without the players list.
data modify storage vaultreset:cur v set from storage vaultreset:tmp cur
data remove storage vaultreset:cur v.players
function vaultreset:expire/check with storage vaultreset:cur v
