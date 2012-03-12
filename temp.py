# TEMPRORARY global state (to be removed)
import pyglet
from util import load_tilegrid

pyglet.font.add_file('data/font.ttf')
pyglet.font.load('eight2empire')

dungeon_tex = load_tilegrid('data/dungeon.png')
creature_tex = load_tilegrid('data/creatures.png')

closed_door_tex = dungeon_tex[9, 3]
open_door_tex = dungeon_tex[8, 3]
floor_tex = dungeon_tex[39, 4]
player_tex = creature_tex[39, 2]
monster_texes = [creature_tex[22, i] for i in xrange(10)]
corpse_texes = [dungeon_tex[2, i] for i in xrange(15)]
wall_tex_row = 33

fountain_anim = pyglet.image.Animation.from_image_sequence(dungeon_tex[11 * dungeon_tex.columns + 15:11 * dungeon_tex.columns + 17], 0.5)
light_anim = pyglet.image.Animation.from_image_sequence(dungeon_tex[11 * dungeon_tex.columns + 17:11 * dungeon_tex.columns + 19], 0.5)
library_texes = [dungeon_tex[17, 14 + i] for i in xrange(6)]

# monkey-patch SpriteGroup's set_state method to disable texture smoothing
_old_set_state = pyglet.sprite.SpriteGroup.set_state
def set_state(self):
    _old_set_state(self)
    pyglet.gl.glTexParameteri(self.texture.target, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)
pyglet.sprite.SpriteGroup.set_state = set_state
