import random
import pyglet
from pyglet.gl import *
from pyglet.window import key

from generator import DungeonGenerator, TILE_FLOOR, TILE_WALL

dungeon = DungeonGenerator((32, 24), 100, (5, 5), (10, 10))
dungeon.generate()

window = pyglet.window.Window(1024, 768, 'Dungeon')
window.set_location(40, 60)

zoom = 4

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
    }

    def is_wall(x, y):
        global dungeon
        if x < 0 or x >= dungeon.size.x or y < 0 or y >= dungeon.size.y:
            return True
        return dungeon.grid[y][x] == TILE_WALL

    v = 0
    if is_wall(x, y - 1):
        v |= n
    if is_wall(x + 1, y):
        v |= e
    if is_wall(x, y + 1):
        v |= s
    if is_wall(x - 1, y):
        v |= w

    return get_dungeon_img_tile(dungeon_img_grid.rows - 3, gridcolmap[v])

map_tiles = []

# prepare map tiles
for x in xrange(dungeon.size.x):
    for y in xrange(dungeon.size.y):
        sx, sy = get_screen_coords(x, y)
        if dungeon.grid[y][x] == TILE_FLOOR:
            img = get_dungeon_img_tile(dungeon_img_grid.rows - 1, 0)
            sprite = pyglet.sprite.Sprite(img, sx, sy, batch=batch)
            sprite.scale = zoom
            map_tiles.append(sprite)
        elif dungeon.grid[y][x] == TILE_WALL:
            img = get_transition_tile(x, y)
            sprite = pyglet.sprite.Sprite(img, sx, sy, batch=batch)
            sprite.scale = zoom
            map_tiles.append(sprite)


@window.event
def on_draw():
    window.clear()
    batch.draw()


@window.event
def on_key_press(sym, mod):
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

pyglet.app.run()
