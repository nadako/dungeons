import random
import pyglet
from pyglet.gl import *
from pyglet.window import key

from generator import DungeonGenerator, TILE_FLOOR, TILE_WALL, TILE_EMPTY

dungeon = DungeonGenerator((40, 25), 100, (3, 3), (10, 10))
dungeon.generate()

zoom = 4

window = pyglet.window.Window(dungeon.size.x * zoom * 8, dungeon.size.y * zoom * 8, 'Dungeon')
window.set_location(40, 60)

dungeon_img = pyglet.image.load('dungeon.png')
dungeon_img_grid = pyglet.image.ImageGrid(dungeon_img, dungeon_img.height / 8, dungeon_img.width / 8)

creatures_img = pyglet.image.load('creatures.png')
creatures_img_grid = pyglet.image.ImageGrid(creatures_img, creatures_img.height / 8, creatures_img.width / 8)

def get_screen_coords(x, y):
    return x * 8 * zoom, window.height - (y + 1) * 8 * zoom

def get_dungeon_img_tile(row, col):
    return dungeon_img_grid[row * dungeon_img_grid.columns + col]

batch = pyglet.graphics.Batch()

starting_room = random.choice(dungeon.rooms)
hero_x = starting_room.position.x + starting_room.size.x / 2
hero_y = starting_room.position.y + starting_room.size.y / 2

hero = pyglet.sprite.Sprite(creatures_img_grid[(creatures_img_grid.rows - 1) * creatures_img_grid.columns + 2], batch=batch)
hero.scale = zoom
hero.set_position(*get_screen_coords(hero_x, hero_y))

def move_hero(dx, dy):
    global hero, hero_x, hero_y
    if dungeon.grid[hero_y + dy][hero_x + dx] == TILE_FLOOR:
        hero_x += dx
        hero_y += dy
        hero.set_position(*get_screen_coords(hero_x, hero_y))

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

    return get_dungeon_img_tile(dungeon_img_grid.rows - 7, gridcolmap[v])

map_tiles = []

floorgroup = pyglet.graphics.OrderedGroup(0)
wallgroup = pyglet.graphics.OrderedGroup(1)

# prepare map tiles
for x in xrange(dungeon.size.x):
    for y in xrange(dungeon.size.y):
        sx, sy = get_screen_coords(x, y)
        if dungeon.grid[y][x] in (TILE_FLOOR, TILE_WALL):
            img = get_dungeon_img_tile(dungeon_img_grid.rows - 1, 4)
            sprite = pyglet.sprite.Sprite(img, sx, sy, batch=batch, group=floorgroup)
            sprite.scale = zoom
            map_tiles.append(sprite)

            if dungeon.grid[y][x] == TILE_WALL:
                img = get_transition_tile(x, y)
                sprite = pyglet.sprite.Sprite(img, sx, sy, batch=batch, group=wallgroup)
                sprite.scale = zoom
                map_tiles.append(sprite)
        elif dungeon.grid[y][x] == TILE_EMPTY:
            img = get_dungeon_img_tile(dungeon_img_grid.rows - 7, 0)
            sprite = pyglet.sprite.Sprite(img, sx, sy, batch=batch, group=wallgroup)
            sprite.scale = zoom
            map_tiles.append(sprite)


@window.event
def on_draw():
    window.clear()
    batch.draw()


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
