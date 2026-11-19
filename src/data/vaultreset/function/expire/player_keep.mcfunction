data modify storage vaultreset:tmp keepp append from storage vaultreset:tmp p
data modify storage vaultreset:tmp keepu append from storage vaultreset:tmp p.u
execute if score #t vaultreset.i < #next vaultreset.i run scoreboard players operation #next vaultreset.i = #t vaultreset.i
