# Reward function of the advancement vaultreset:unlocked. @s = the player who
# just put a trial key into a vault.
advancement revoke @s only vaultreset:unlocked
data modify storage vaultreset:tmp uuid set from entity @s UUID

# 30 steps of 0.2 blocks = 6 blocks, slightly more than the reach in creative
# mode. The player just clicked the block, so it is in line of sight - an
# occlusion check would be pure cosmetics here.
scoreboard players set #ray vaultreset.i 30
execute anchored eyes positioned ^ ^ ^ run function vaultreset:register/ray
