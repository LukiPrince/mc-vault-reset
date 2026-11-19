# Runs only when #clock has reached the smallest expiry value.
# The list is rebuilt during the pass: whatever remains appends itself again.
scoreboard players operation #next vaultreset.i = #max vaultreset.i
data modify storage vaultreset:tmp work set from storage vaultreset:data vaults
data modify storage vaultreset:data vaults set value []
function vaultreset:expire/next

# Empty list = chance to reset the counter. This keeps #clock small for good
# and the int overflow out of normal operation.
execute unless data storage vaultreset:data vaults[0] run scoreboard players set #clock vaultreset.i 0
execute unless data storage vaultreset:data vaults[0] run scoreboard players operation #next vaultreset.i = #max vaultreset.i
