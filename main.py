import random
from collections import defaultdict, deque

from shadowcaster import ShadowCaster

def integer_triangular(a, b):
    return int(round(random.triangular(a, b)))

TILE_EMPTY = ' '
TILE_WALL = '#'
TILE_FLOOR = '.'
TILE_DOOR_CLOSED = '+'
TILE_DOOR_OPEN = '/'

class LevelObject(object):

    blocks_sight = False
    blocks_movement = False

    def __init__(self, **components):
        self.x = None
        self.y = None
        self.level = None

        for name, value in components.items():
            setattr(self, name, value)
            value.owner = self

    def bump(self, who):
        pass

class Level(object):

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.grid = [TILE_EMPTY for _ in xrange(size_x * size_y)]
        self.rooms = []
        self.objects = defaultdict(list)
        self.actors = deque()

    def blocks_sight(self, x, y):
        if not self.in_bounds(x, y):
            return True

        if self.get_tile(x, y) == TILE_WALL:
            return True

        if (x, y) in self.objects:
            for object in self.objects[x, y]:
                if object.blocks_sight:
                    return object

        return False

    def blocks_movement(self, x, y):
        if not self.in_bounds(x, y):
            return True

        if self.get_tile(x, y) == TILE_WALL:
            return True

        if (x, y) in self.objects:
            for object in self.objects[x, y]:
                if object.blocks_movement:
                    return object

        return False

    def get_tile(self, x, y):
        return self.grid[y * self.size_x + x]

    def set_tile(self, x, y, tile):
        if tile in (TILE_DOOR_CLOSED, TILE_DOOR_OPEN):
            is_open = (tile == TILE_DOOR_OPEN)
            tile = TILE_FLOOR
            self.add_object(Door(is_open), x, y)

        self.grid[y * self.size_x + x] = tile

    def in_bounds(self, x, y):
        return x >= 0 and x < self.size_x and y >= 0 and y < self.size_y

    def add_object(self, obj, x, y):
        self.objects[x, y].append(obj)
        obj.x = x
        obj.y = y
        obj.level = self

        actor = getattr(obj, 'actor', None)
        if actor:
            self.actors.append(actor)

    def remove_object(self, obj):
        self.objects[obj.x, obj.y].remove(obj)
        obj.x = None
        obj.y = None
        obj.level = None

        actor = getattr(obj, 'actor', None)
        if actor:
            self.actors.remove(actor)

    def move_object(self, obj, x, y):
        self.objects[obj.x, obj.y].remove(obj)
        self.objects[x, y].append(obj)
        obj.x = x
        obj.y = y

    def tick(self):
        if self.actors:
            actor = self.actors[0]
            self.actors.rotate()
            actor.energy += actor.speed
            while actor.energy > 0:
                actor.energy -= actor.act()

class Room(object):

    def __init__(self, tiles):
        self.size_x = len(tiles[0])
        self.size_y = len(tiles)
        self.tiles = tiles
        self.x = None
        self.y = None

DIR_N = (0, -1)
DIR_S = (0, 1)
DIR_W = (-1, 0)
DIR_E = (1, 0)

class LevelGenerator(object):

    def __init__(self, level):
        self.level = level

    def create_room(self):
        size_x = random.randint(7, 12)
        size_y = random.randint(7, 12)
        tiles = []
        for y in xrange(size_y):
            row = []
            for x in xrange(size_x):
                if x == 0 or x == size_x - 1 or y == 0 or y == size_y - 1:
                    row.append(TILE_WALL)
                else:
                    row.append(TILE_FLOOR)
            tiles.append(row)
        return Room(tiles)

    def place_room(self, room, x, y):
        room.x = x
        room.y = y
        self.level.rooms.append(room)

        for row in room.tiles:
            for tile in row:
                if tile == TILE_EMPTY:
                    continue
                self.level.set_tile(x, y, tile)
                x += 1
            y += 1
            x = room.x

    def choose_gate(self):
        room = random.choice(self.level.rooms)
        dir = random.choice((DIR_N, DIR_S, DIR_W, DIR_E))

        if dir is DIR_N:
            x = integer_triangular(room.x + 1, room.x + room.size_x - 2)
            y = room.y
        elif dir is DIR_S:
            x = integer_triangular(room.x + 1, room.x + room.size_x - 2)
            y = room.y + room.size_y - 1
        elif dir is DIR_W:
            x = room.x
            y = integer_triangular(room.y + 1, room.y + room.size_y - 2)
        elif dir is DIR_E:
            x = room.x + room.size_x - 1
            y = integer_triangular(room.y + 1, room.y + room.size_y - 2)

        return int(round(x)), int(round(y)), dir

    def has_space_for_room(self, room, x, y):
        if x < 0 or x + room.size_x > self.level.size_x or y < 0 or y + room.size_y > self.level.size_y:
            return False

        x1 = x
        for row in room.tiles:
            for tile in row:
                if (tile != TILE_EMPTY) and (self.level.get_tile(x, y) != TILE_EMPTY):
                    return False
                x +=1
            y += 1
            x = x1
        return True

    def connect_rooms(self, x, y, dir):
        tiles = [TILE_FLOOR, TILE_FLOOR]

        if random.random() < 0.75:
            tile = random.random() < 0.1 and TILE_DOOR_OPEN or TILE_DOOR_CLOSED
            tiles[random.randint(0, 1)] = tile

        self.level.set_tile(x, y, tiles[0])
        self.level.set_tile(x + dir[0], y + dir[1], tiles[1])

    def generate(self):
        room = self.create_room()
        x = (self.level.size_x - room.size_x) / 2
        y = (self.level.size_y - room.size_y) / 2
        self.place_room(room, x, y)

        for i in xrange(self.level.size_x * self.level.size_y * 2):
            room = self.create_room()
            x, y, dir = self.choose_gate()

            if dir is DIR_N:
                room_x = x - integer_triangular(1, room.size_x - 2)
                room_y = y - room.size_y
            elif dir is DIR_S:
                room_x = x - integer_triangular(1, room.size_x - 2)
                room_y = y + 1
            elif dir is DIR_W:
                room_x = x - room.size_x
                room_y = y - integer_triangular(1, room.size_y - 1)
            elif dir is DIR_E:
                room_x = x + 1
                room_y = y - integer_triangular(1, room.size_y - 1)

            if self.has_space_for_room(room, room_x, room_y):
                self.place_room(room, room_x, room_y)
                self.connect_rooms(x, y, dir)

import pyglet
import greenlet
from pyglet.window import key

def load_tilegrid(name):
    img = pyglet.resource.image(name)
    grid = pyglet.image.ImageGrid(img, img.height / 8, img.width / 8)
    return grid.get_texture_sequence()

dungeon_tex = load_tilegrid('dungeon.png')
creature_tex = load_tilegrid('creatures.png')

floor_tex = dungeon_tex[39, 4]
wall_tex = dungeon_tex[33, 20]
player_tex = creature_tex[39, 2]
monster_tex = creature_tex[22, 1]
closed_door_tex = dungeon_tex[9, 3]
open_door_tex = dungeon_tex[8, 3]


class Component(object):

    owner = None

class Actor(Component):

    def __init__(self, speed, act=None):
        self.energy = 0
        self.speed = speed
        self._act = act

    def act(self):
        if self._act is None:
            raise NotImplementedError()
        return self._act(self)

class FOV(Component):

    def __init__(self, radius):
        self.radius = radius
        self.lightmap = {}
        self.memento = set()

    def update_light(self):
        self.lightmap.clear()
        self.lightmap[self.owner.x, self.owner.y] = 1
        caster = ShadowCaster(self.owner.level.blocks_sight, self.set_light)
        caster.calculate_light(self.owner.x, self.owner.y, self.radius)

    def set_light(self, x, y, intensity):
        self.lightmap[x, y] = intensity
        self.memento.add((x, y))

    def is_in_fov(self, x, y):
        return self.lightmap.get((x, y), 0) > 0

class Movement(Component):

    def move(self, dx, dy):
        new_x = self.owner.x + dx
        new_y = self.owner.y + dy

        blocker = self.owner.level.blocks_movement(new_x, new_y)
        if not blocker:
            self.owner.level.move_object(self.owner, new_x, new_y)
        elif isinstance(blocker, LevelObject):
            blocker.bump(self.owner)

        # TODO: use some kind of events/signals
        if hasattr(self.owner, 'fov'):
            self.owner.fov.update_light()

class Renderable(Component):

    def __init__(self, tex):
        self.sprite = pyglet.sprite.Sprite(tex)



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

class DoorRenderable(Component):

    def __init__(self):
        self.open_sprite = pyglet.sprite.Sprite(open_door_tex)
        self.closed_sprite = pyglet.sprite.Sprite(closed_door_tex)

    @property
    def sprite(self):
        return self.owner.is_open and self.open_sprite or self.closed_sprite

class Door(LevelObject):

    def __init__(self, is_open):
        self.is_open = is_open
        super(Door, self).__init__(renderable=DoorRenderable())

    @property
    def blocks_sight(self):
        return not self.is_open

    @property
    def blocks_movement(self):
        return not self.is_open

    def bump(self, who):
        self.is_open = not self.is_open

level = Level(70, 50)
generator = LevelGenerator(level)
generator.generate()

player = LevelObject(actor=Actor(100, player_act), fov=FOV(10), movement=Movement(), renderable=Renderable(player_tex))
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

        monster = LevelObject(actor=Actor(100, monster_act), movement=Movement(), renderable=Renderable(monster_tex))
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


def prepare_level_sprites(level):
    rows = []
    for y in xrange(level.size_y):
        row = []
        for x in xrange(level.size_x):
            tile = level.get_tile(x, y)
            if tile == TILE_WALL:
                sprite = pyglet.sprite.Sprite(wall_tex, x * 8, y * 8)
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
                if hasattr(obj, 'renderable'):
                    sprite = obj.renderable.sprite
                    break

        if sprite is not None:
            glPushMatrix()
            glTranslatef(x * 8, y * 8, 0)
            sprite.draw()
            glPopMatrix()

pyglet.app.run()
