# Chunk not loaded: keep the entry unchanged and try again next cycle. Only
# lower #next, never raise it - an earlier expiry elsewhere must not be pushed
# back by this.
data modify storage vaultreset:data vaults append from storage vaultreset:tmp cur
scoreboard players operation #retry vaultreset.i = #clock vaultreset.i
scoreboard players add #retry vaultreset.i 100
execute if score #retry vaultreset.i < #next vaultreset.i run scoreboard players operation #next vaultreset.i = #retry vaultreset.i
