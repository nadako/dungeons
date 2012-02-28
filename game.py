import random
import pyglet
from pyglet.gl import *
from pyglet.window import key

from generator import DungeonGenerator, TILE_FLOOR, TILE_WALL, TILE_EMPTY
from eight2empire import TRANSITION_TILES
from graphics import TextureGroup, ShaderGroup
from shader import Shader

TILE_SIZE = 8
ZOOM = 4
WALL_TEX_ROW = 33
FLOOR_TEX = 39, 4
HERO_TEX = 39, 2

dungeon_img = pyglet.image.load('dungeon.png')
dungeon_seq = pyglet.image.ImageGrid(dungeon_img, dungeon_img.height / TILE_SIZE, dungeon_img.width / TILE_SIZE)
dungeon_tex = dungeon_seq.get_texture_sequence()

creatures_img = pyglet.image.load('creatures.png')
creatures_seq = pyglet.image.ImageGrid(creatures_img, creatures_img.height / TILE_SIZE, creatures_img.width / TILE_SIZE)
creatures_tex = creatures_seq.get_texture_sequence()

dungeon = DungeonGenerator((30, 25), 100, (3, 3), (10, 10))
dungeon.generate()

window = pyglet.window.Window(dungeon.size.x * TILE_SIZE * ZOOM, dungeon.size.y * TILE_SIZE * ZOOM, 'Dungeon')
window.set_location(40, 60)

batch = pyglet.graphics.Batch()

starting_room = random.choice(dungeon.rooms)
hero_x = starting_room.position.x + starting_room.size.x / 2
hero_y = starting_room.position.y + starting_room.size.y / 2

def move_hero(dx, dy):
    global hero_x, hero_y
    if dungeon.grid[hero_y + dy][hero_x + dx] == TILE_FLOOR:
        hero_x += dx
        hero_y += dy

def is_wall(x, y):
    if x < 0 or x >= dungeon.size.x or y < 0 or y >= dungeon.size.y:
        return True
    return dungeon.grid[y][x] in (TILE_WALL, TILE_EMPTY)

def get_transition_tile(x, y):
    n = 1
    e = 2
    s = 4
    w = 8
    nw = 128
    ne = 16
    se = 32
    sw = 64

    v = 0
    if is_wall(x, y + 1):
        v |= n
    if is_wall(x + 1, y):
        v |= e
    if is_wall(x, y - 1):
        v |= s
    if is_wall(x - 1, y):
        v |= w
    if is_wall(x - 1, y + 1):
        v |= nw
    if is_wall(x + 1, y + 1):
        v |= ne
    if is_wall(x - 1, y - 1):
        v |= sw
    if is_wall(x + 1, y - 1):
        v |= se

    if v not in TRANSITION_TILES:
        v &= 15

    return dungeon_tex[WALL_TEX_ROW, TRANSITION_TILES[v]]

class HeroGroup(pyglet.graphics.Group):

    def __init__(self, parent=None):
        super(HeroGroup, self).__init__(parent)

    def set_state(self):
        glPushMatrix()
        glTranslatef(hero_x * 8, hero_y * 8, 0)

    def unset_state(self):
        glPopMatrix()

hero_vlist = batch.add(4, GL_QUADS, HeroGroup(TextureGroup(creatures_tex, pyglet.graphics.OrderedGroup(1))),
    ('v2i/statc', (0, 0, TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, 0, TILE_SIZE)),
    ('t3f/statc', creatures_tex[HERO_TEX].tex_coords)
)

def get_draw_order():
    result = []
    for y, row in enumerate(dungeon.grid):
        for x, tile in enumerate(row):
            if tile == TILE_EMPTY:
                result.append((x, y, TILE_EMPTY))
            else:
                result.append((x, y, TILE_FLOOR))
                if tile == TILE_WALL:
                    result.append((x, y, TILE_WALL))
    return result

def prepare_tile_vertices(draw_order):
    vertices = []
    tex_coords = []
    floor_tex = dungeon_tex[FLOOR_TEX]
    empty_tex = dungeon_tex[WALL_TEX_ROW, 0]

    for x, y, tile in draw_order:
        x1 = x * TILE_SIZE
        x2 = x1 + TILE_SIZE
        y1 = y * TILE_SIZE
        y2 = y1 + TILE_SIZE
        vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))

        if tile == TILE_WALL:
            tex = get_transition_tile(x, y)
        elif tile == TILE_FLOOR:
            tex = floor_tex
        else:
            tex = empty_tex
        tex_coords.extend(tex.tex_coords)

    return vertices, tex_coords

map_shader = Shader(
("""
void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
""").split('\n'),
"""
uniform sampler2D texture;
void main()
{
    gl_FragColor = texture2D(texture, gl_TexCoord[0].st);
}
""".split('\n'))


draw_order = get_draw_order()
vertices, tex_coords = prepare_tile_vertices(draw_order)

map_vlist = batch.add(len(draw_order) * 4, GL_QUADS, ShaderGroup(map_shader, TextureGroup(dungeon_tex, pyglet.graphics.OrderedGroup(0))),
    ('v2f/static', vertices),
    ('t3f/static', tex_coords),
)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

@window.event
def on_draw():
    window.clear()

    glPushMatrix()
    glScalef(ZOOM, ZOOM, 1)
    batch.draw()
    glPopMatrix()


def process_keys():
    while True:
        sym, mod = yield

        if sym == key.NUM_8:
            move_hero(0, 1)
        elif sym == key.NUM_2:
            move_hero(0, -1)
        elif sym == key.NUM_4:
            move_hero(-1, 0)
        elif sym == key.NUM_6:
            move_hero(1, 0)
        elif sym == key.NUM_7:
            move_hero(-1, 1)
        elif sym == key.NUM_9:
            move_hero(1, 1)
        elif sym == key.NUM_1:
            move_hero(-1, -1)
        elif sym == key.NUM_3:
            move_hero(1, -1)

key_processor = process_keys()
key_processor.send(None) # start the coroutine

@window.event
def on_key_press(sym, mod):
    key_processor.send((sym, mod))

pyglet.app.run()
