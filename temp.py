# TEMPRORARY global state (to be removed)
from util import load_tilegrid


dungeon_tex = load_tilegrid('data/dungeon.png')
creature_tex = load_tilegrid('data/creatures.png')

closed_door_tex = dungeon_tex[9, 3]
open_door_tex = dungeon_tex[8, 3]
floor_tex = dungeon_tex[39, 4]
player_tex = creature_tex[39, 2]
monster_tex = creature_tex[22, 1]
wall_tex_row = 33
