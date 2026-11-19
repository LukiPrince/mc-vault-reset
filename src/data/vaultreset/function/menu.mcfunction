# /function vaultreset:menu - permission level 2 by default, so ops only.
# Opens a native dialog window (since 1.21.6). No item, no chat history.

execute store result score #cd vaultreset.i run data get storage vaultreset:data config.cooldown
scoreboard players operation #cd vaultreset.i /= #20 vaultreset.i
execute store result storage vaultreset:tmp secs int 1 run scoreboard players get #cd vaultreset.i
function vaultreset:util/fmt

# Start value of the slider, clamped to its range.
scoreboard players operation #init vaultreset.i = #cd vaultreset.i
execute if score #init vaultreset.i matches ..4 run scoreboard players set #init vaultreset.i 5
execute if score #init vaultreset.i matches 7201.. run scoreboard players set #init vaultreset.i 7200
execute store result storage vaultreset:tmp init int 1 run scoreboard players get #init vaultreset.i

# "data get" on a list returns its length.
execute store result score #n vaultreset.i run data get storage vaultreset:data vaults
execute store result storage vaultreset:tmp n int 1 run scoreboard players get #n vaultreset.i

# Dialog templates use the same $(...) syntax as macro functions. The
# placeholder for the slider value must therefore survive the macro step
# unchanged: this line is NOT a macro line (no leading $), so "$(secs)" stays
# literal here and is inserted in menu/show as $(ph).
data modify storage vaultreset:tmp ph set value "$(secs)"

function vaultreset:menu/show with storage vaultreset:tmp
