import random
import pyglet
from pyglet.gl import *
from pyglet.window import key

from generator import DungeonGenerator, TILE_FLOOR, TILE_WALL, TILE_EMPTY
from shader import Shader

dungeon = DungeonGenerator((30, 25), 100, (3, 3), (10, 10))
dungeon.generate()

zoom = 4

window = pyglet.window.Window(dungeon.size.x * zoom * 8, dungeon.size.y * zoom * 8, 'Dungeon')
window.set_location(40, 60)

dungeon_img = pyglet.image.load('dungeon.png')
dungeon_seq = pyglet.image.ImageGrid(dungeon_img, dungeon_img.height / 8, dungeon_img.width / 8)
dungeon_tex = dungeon_seq.get_texture_sequence()

creatures_img = pyglet.image.load('creatures.png')
creatures_seq = pyglet.image.ImageGrid(creatures_img, creatures_img.height / 8, creatures_img.width / 8)
creatures_tex = creatures_seq.get_texture_sequence()

def get_screen_coords(x, y):
    return x * 8, window.height - (y + 1) * 8

batch = pyglet.graphics.Batch()

starting_room = random.choice(dungeon.rooms)
hero_x = starting_room.position.x + starting_room.size.x / 2
hero_y = starting_room.position.y + starting_room.size.y / 2

def move_hero(dx, dy):
    global hero, hero_x, hero_y
    if dungeon.grid[hero_y + dy][hero_x + dx] == TILE_FLOOR:
        hero_x += dx
        hero_y += dy

def get_transition_tile(x, y):
    n = 1
    e = 2
    s = 4
    w = 8
    nw = 128
    ne = 16
    se = 32
    sw = 64
    gridcolmap = {
        0: 20,
        n: 13,
        e: 14,
        n+e: 10,
        s: 12,
        s+n: 4,
        e+s: 16,
        e+s+n: 3,
        w: 15,
        w+n: 11,
        e+w: 1,
        e+w+n: 1,
        s+w: 17,
        s+w+n: 2,
        s+w+e: 0,
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

    def is_wall(x, y):
        global dungeon
        if x < 0 or x >= dungeon.size.x or y < 0 or y >= dungeon.size.y:
            return True
        return dungeon.grid[y][x] in (TILE_WALL, TILE_EMPTY)

    v = 0
    if is_wall(x, y - 1):
        v |= n
    if is_wall(x + 1, y):
        v |= e
    if is_wall(x, y + 1):
        v |= s
    if is_wall(x - 1, y):
        v |= w
    if is_wall(x - 1, y - 1):
        v |= nw
    if is_wall(x + 1, y - 1):
        v |= ne
    if is_wall(x - 1, y + 1):
        v |= sw
    if is_wall(x + 1, y + 1):
        v |= se

    if v not in gridcolmap:
        v = v & 15

    return dungeon_tex[dungeon_tex.rows - 7, gridcolmap[v]]

class TextureGroup(pyglet.graphics.TextureGroup):

    def set_state(self):
        super(TextureGroup, self).set_state()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

class HeroGroup(pyglet.graphics.Group):

    def __init__(self, parent=None):
        super(HeroGroup, self).__init__(parent)

    def set_state(self):
        glPushMatrix()
        x, y = get_screen_coords(hero_x, hero_y)
        glTranslatef(x, y, 0)

    def unset_state(self):
        glPopMatrix()

hero_vlist = batch.add(4, GL_QUADS, HeroGroup(TextureGroup(creatures_tex, pyglet.graphics.OrderedGroup(1))),
    ('v2i/statc', (0, 0, 8, 0, 8, 8, 0, 8)),
    ('t3f/statc', creatures_tex[creatures_tex.rows - 1, 0].tex_coords)
)

num_tiles = 0
vertices = []
tex_coords = []
floor_tex = dungeon_tex[dungeon_tex.rows - 1, 4]
empty_tex = dungeon_tex[dungeon_tex.rows - 7, 0]

for tile_y, row in enumerate(dungeon.grid):
    for tile_x, tile in enumerate(row):
        x1, y1 = get_screen_coords(tile_x, tile_y)
        x2, y2 = x1 + 8, y1 + 8

        num_tiles += 1
        vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
        if tile == TILE_EMPTY:
            tex_coords.extend(empty_tex.tex_coords)
        else:
            tex_coords.extend(floor_tex.tex_coords)

        if tile == TILE_WALL:
            num_tiles += 1
            vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
            tex = get_transition_tile(tile_x, tile_y)
            tex_coords.extend(tex.tex_coords)

map_vlist = batch.add(num_tiles * 4, GL_QUADS, TextureGroup(dungeon_tex, pyglet.graphics.OrderedGroup(0)),
    ('v2f/static', vertices),
    ('t3f/static', tex_coords)
)

shader = Shader(
    """
    void main()
    {
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        gl_TexCoord[0] = gl_MultiTexCoord0;
    }
    """.split('\n'),
    """
    uniform sampler2D texture;

    void main()
    {
        gl_FragColor = texture2D(texture, gl_TexCoord[0].st);
    }
    """.split('\n'))

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

@window.event
def on_draw():
    window.clear()

    glPushMatrix()
    glScalef(zoom, zoom, 1)
    glTranslatef(0, -dungeon.size.y * 8 * (zoom - 1), 0)
    with shader:
        batch.draw()
    glPopMatrix()


def process_keys():
    while True:
        sym, mod = yield

        if sym == key.NUM_8:
            move_hero(0, -1)
        elif sym == key.NUM_2:
            move_hero(0, 1)
        elif sym == key.NUM_4:
            move_hero(-1, 0)
        elif sym == key.NUM_6:
            move_hero(1, 0)
        elif sym == key.NUM_7:
            move_hero(-1, -1)
        elif sym == key.NUM_9:
            move_hero(1, -1)
        elif sym == key.NUM_1:
            move_hero(-1, 1)
        elif sym == key.NUM_3:
            move_hero(1, 1)

key_processor = process_keys()
key_processor.send(None) # start the coroutine

@window.event
def on_key_press(sym, mod):
    key_processor.send((sym, mod))

pyglet.app.run()
