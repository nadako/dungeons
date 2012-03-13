# TEMPRORARY global state (to be removed)
import pyglet

from util import load_tilegrid


# monkey-patch SpriteGroup's set_state method to disable texture smoothing
_old_set_state = pyglet.sprite.SpriteGroup.set_state
def set_state(self):
    _old_set_state(self)
    pyglet.gl.glTexParameteri(self.texture.target, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)
pyglet.sprite.SpriteGroup.set_state = set_state


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

fountain_anim = pyglet.image.Animation.from_image_sequence(dungeon_tex[11 * dungeon_tex.columns + 15:11 * dungeon_tex.columns + 17], 0.5)
light_anim = pyglet.image.Animation.from_image_sequence(dungeon_tex[11 * dungeon_tex.columns + 17:11 * dungeon_tex.columns + 19], 0.5)
library_texes = [dungeon_tex[17, 14 + i] for i in xrange(6)]


def get_wall_tex(transition):
    if transition not in WALL_TRANSITION_TILES:
        transition &= 15
    return dungeon_tex[33, WALL_TRANSITION_TILES[transition]]

WALL_TRANSITION_TILES = {
    0: 20,
    1: 13,
    2: 14,
    3: 10,
    4: 12,
    5: 4,
    6: 16,
    7: 3,
    8: 15,
    9: 11,
    10: 1,
    11: 1,
    12: 17,
    13: 2,
    14: 0,
    15: 0,

    19: 10,
    131: 10,
    147: 10,
    227: 10,
    243: 10,
    51: 10,
    35: 10,

    137: 11,
    153: 11,
    201: 11,
    217: 11,
    233: 11,
    249: 11,

    63: 7,
    46: 7,
    174: 7,
    175: 7,
    190: 7,
    191: 7,
    62: 7,
    47: 7,

    76: 17,
    108: 17,
    204: 17,
    124: 17,
    220: 17,
    92: 17,
    236: 17,
    252: 17,

    39: 3,
    103: 3,
    231: 3,
    55: 3,
    183: 3,
    119: 3,
    167: 3,
    247: 3,

    78: 6,
    206: 6,
    222: 6,
    223: 6,
    94: 6,
    95: 6,
    79: 6,
    207: 6,

    26: 1,
    27: 1,
    42: 1,
    106: 1,
    123: 1,
    138: 1,
    139: 1,
    155: 1,
    171: 1,
    187: 1,
    203: 1,
    219: 1,
    235: 1,
    251: 1,

    159: 5,
    143: 5,

    38: 16,
    102: 16,
    54: 16,
    118: 16,
    246: 16,
    230: 16,

    125: 2,
    221: 2,
    93: 2,
    205: 2,
    237: 2,
    253: 2,
    109: 2,
    77: 2,

    64: 20,
    80: 20,
    90: 20,
    160: 20,
    176: 20,
    224: 20,
    240: 20,


    30: 0,
    110: 0,
    111: 0,
    126: 0,
    127: 0,
    238: 0,
    239: 0,
    254: 0,
    255: 0,
}
