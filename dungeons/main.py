import random
from dungeons.level import Level, Renderable, Movement, FOV, Actor, LevelObject
from dungeons.level_generator import LevelGenerator, TILE_WALL, TILE_EMPTY, TILE_FLOOR

import pyglet
import greenlet
from pyglet.window import key
from dungeons.temp import player_tex, monster_tex, dungeon_tex, wall_tex_row, floor_tex
from eight2empire import TRANSITION_TILES

def player_act(actor):
    player = actor.owner
    sym = wait_key()
    if sym == key.NUM_8:
        player.movement.move(0, 1)
    elif sym == key.NUM_2:
        player.movement.move(0, -1)
    elif sym == key.NUM_4:
        player.movement.move(-1, 0)
    elif sym == key.NUM_6:
        player.movement.move(1, 0)
    elif sym == key.NUM_7:
        player.movement.move(-1, 1)
    elif sym == key.NUM_9:
        player.movement.move(1, 1)
    elif sym == key.NUM_1:
        player.movement.move(-1, -1)
    elif sym == key.NUM_3:
        player.movement.move(1, -1)
    elif sym == key.ESCAPE:
        raise ExitGame()
    return 100

def monster_act(actor):
    dx = random.randint(-1, 1)
    dy = random.randint(-1, 1)
    actor.owner.movement.move(dx, dy)
    return 100

class ExitGame(Exception):
    pass

level = Level(70, 50)
generator = LevelGenerator(level)
generator.generate()

player = LevelObject(Actor(100, player_act), FOV(10), Movement(), Renderable(player_tex))
player.blocks_movement = True

room = random.choice(level.rooms)
level.add_object(player, room.x + room.size_x / 2, room.y + room.size_y / 2)
player.fov.update_light()

for room in level.rooms:
    for i in xrange(random.randint(0, 5)):
        x = random.randrange(room.x, room.x + room.size_x)
        y = random.randrange(room.y, room.y + room.size_y)

        if (x, y) in level.objects and level.objects[x, y]:
            continue

        monster = LevelObject(Actor(100, monster_act), Movement(), Renderable(monster_tex))
        monster.blocks_movement = True
        level.add_object(monster, x, y)


window = pyglet.window.Window(800, 600, 'Dungeon')

def wait_key():
    sym = greenlet.getcurrent().parent.switch()
    return sym

def processor():
    while True:
        try:
            level.tick()
        except ExitGame:
            break

g_processor = greenlet.greenlet(processor)
g_processor.switch()

@window.event
def on_key_press(sym, mod):
    g_processor.switch(sym)

from pyglet.gl import *

def get_transition_tile(x, y):
    n = 1
    e = 2
    s = 4
    w = 8
    nw = 128
    ne = 16
    se = 32
    sw = 64

    def is_wall(x, y):
        if not level.in_bounds(x, y):
            return True
        return level.get_tile(x, y) in (TILE_WALL, TILE_EMPTY)

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

    return dungeon_tex[wall_tex_row, TRANSITION_TILES[v]]

def prepare_level_sprites(level):
    rows = []
    for y in xrange(level.size_y):
        row = []
        for x in xrange(level.size_x):
            tile = level.get_tile(x, y)
            if tile == TILE_WALL:
                tex = get_transition_tile(x, y)
                sprite = pyglet.sprite.Sprite(tex, x * 8, y * 8)
            elif tile == TILE_FLOOR:
                sprite = pyglet.sprite.Sprite(floor_tex, x * 8, y * 8)
            else:
                sprite = None
            row.append(sprite)
        rows.append(row)
    return rows

level_sprites = prepare_level_sprites(level)

@window.event
def on_draw():
    window.clear()

    for x, y in player.fov.lightmap:
        level_sprite = level_sprites[y][x]
        if level_sprite:
            level_sprite.draw()

        sprite = None

        if (x, y) in level.objects and len(level.objects[x, y]) > 0:
            for obj in level.objects[x, y]:
                if hasattr(obj, Renderable.component_name):
                    sprite = obj.renderable.sprite
                    break

        if sprite is not None:
            glPushMatrix()
            glTranslatef(x * 8, y * 8, 0)
            sprite.draw()
            glPopMatrix()

pyglet.app.run()
