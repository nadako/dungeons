import greenlet
import random
import pyglet
from pyglet.gl import *
from pyglet.window import key
from dungeon import TileGrid, TileType, Door

from generator import DungeonGenerator
from eight2empire import TRANSITION_TILES
from graphics import TextureGroup, ShaderGroup
from shader import Shader
from shadowcaster import ShadowCaster
from timing import ACTION_COST, Actor, TimeSystem

TILE_SIZE = 8
ZOOM = 4
WALL_TEX_ROW = 33
FLOOR_TEX = 39, 4
HERO_TEX = 39, 2
LIGHT_RADIUS = 10
CLOSED_DOOR_TEX = 9, 3
OPEN_DOOR_TEX = 8, 3

dungeon_img = pyglet.image.load('dungeon.png')
dungeon_seq = pyglet.image.ImageGrid(dungeon_img, dungeon_img.height / TILE_SIZE, dungeon_img.width / TILE_SIZE)
dungeon_tex = dungeon_seq.get_texture_sequence()
open_door_tex = dungeon_tex[OPEN_DOOR_TEX]
closed_door_tex = dungeon_tex[CLOSED_DOOR_TEX]

creatures_img = pyglet.image.load('creatures.png')
creatures_seq = pyglet.image.ImageGrid(creatures_img, creatures_img.height / TILE_SIZE, creatures_img.width / TILE_SIZE)
creatures_tex = creatures_seq.get_texture_sequence()

tile_grid = TileGrid(100, 100)
dungeon = DungeonGenerator(tile_grid, min_room_size=(6, 6), max_room_size=(20, 20), door_chance=50)
dungeon.generate()
dungeon.print_dungeon()

window = pyglet.window.Window(1024, 768, 'Dungeon')
window.set_location(40, 60)

center_anchor_x = window.width / 2 / ZOOM
center_anchor_y = window.height / 2 / ZOOM

batch = pyglet.graphics.Batch()

starting_room = random.choice(dungeon.rooms)
hero_x = starting_room.position.x + starting_room.size.x / 2
hero_y = starting_room.position.y + starting_room.size.y / 2

def move_hero(dx, dy):
    global hero_x, hero_y
    tile = tile_grid[hero_x + dx, hero_y + dy]
    if tile.is_passable:
        hero_x += dx
        hero_y += dy
    else:
        tile.bump(None)
    update_lighting()

def in_bounds(x, y):
    if x < 0 or x >= tile_grid.size_x or y < 0 or y >= tile_grid.size_y:
        return False
    return True

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
        if not in_bounds(x, y):
            return True
        return tile_grid[x, y].type in (TileType.WALL, TileType.EMPTY)

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
        glTranslatef(center_anchor_x, center_anchor_y, 0)

    def unset_state(self):
        glPopMatrix()

hero_vlist = batch.add(4, GL_QUADS, HeroGroup(TextureGroup(creatures_tex, pyglet.graphics.OrderedGroup(1))),
    ('v2i/statc', (0, 0, TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, 0, TILE_SIZE)),
    ('t3f/statc', creatures_tex[HERO_TEX].tex_coords)
)

def get_draw_order():
    result = []
    for x in xrange(tile_grid.size_x):
        for y in xrange(tile_grid.size_y):
            result.append((x, y, TileType.FLOOR))
            if tile_grid[x, y].type == TileType.WALL:
                result.append((x, y, TileType.WALL))
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

        if tile == TileType.WALL:
            tex = get_transition_tile(x, y)
        elif tile == TileType.FLOOR:
            tex = floor_tex
        else:
            tex = empty_tex
        tex_coords.extend(tex.tex_coords)

    return vertices, tex_coords

explored = {}
lightmap = {}

MIN_LIGHT = 0.3

def is_in_fov(x, y):
    return lightmap.get((x, y), 0) > 0

def adjust_light(intensity):
    return MIN_LIGHT + (1.0 - MIN_LIGHT) * intensity

def prepare_lighting():
    global hero_x, hero_y, draw_order, explored, lightmap

    lightmap.clear()
    lightmap[hero_x, hero_y] = 1
    def set_light(x, y, intensity):
        global lightmap, explored
        lightmap[x, y] = intensity
        if intensity > 0:
            explored[x, y] = True

    def blocks_light(x, y):
        if not in_bounds(x, y):
            return False
        return not tile_grid[x, y].is_transparent

    caster = ShadowCaster(blocks_light, set_light)
    caster.calculate_light(hero_x, hero_y, LIGHT_RADIUS)

    buffer = []
    for x, y, tile in draw_order:
        l = lightmap.get((x, y), 0)

        if l > 0:
            l = adjust_light(l)
        elif explored.get((x, y)):
            l = MIN_LIGHT

        for _ in xrange(4):
            buffer.extend((int(l * 255), ) * 3)

    return buffer

def draw_tile_objects():
    starty = max(0, hero_y - LIGHT_RADIUS)
    endy = min(hero_y + LIGHT_RADIUS, tile_grid.size_y)
    startx = max(0, hero_x - LIGHT_RADIUS)
    endx = min(hero_x + LIGHT_RADIUS, tile_grid.size_x)

    for x in xrange(startx, endx):
        for y in xrange(starty, endy):
            if not is_in_fov(x, y):
                continue
            objects = tile_grid[x, y].objects
            if not objects:
                continue
            object = objects[0]
            if isinstance(object, Door):
                glPushMatrix()
                glTranslatef(x * TILE_SIZE + center_anchor_x - hero_x * TILE_SIZE, y * TILE_SIZE + center_anchor_y - hero_y * TILE_SIZE, 0)
                if object.is_open:
                    open_door_tex.blit(0, 0)
                else:
                    closed_door_tex.blit(0, 0)
                glPopMatrix()


map_shader = Shader([open('map.vert', 'r').read()], [open('map.frag', 'r').read()])
draw_order = get_draw_order()
vertices, tex_coords = prepare_tile_vertices(draw_order)

class MapGroup(pyglet.graphics.Group):

    def __init__(self, parent=None):
        super(MapGroup, self).__init__(parent)

    def set_state(self):
        glPushMatrix()
        glTranslatef(center_anchor_x - hero_x * TILE_SIZE, center_anchor_y - hero_y * TILE_SIZE, 0)

    def unset_state(self):
        glPopMatrix()

map_vlist = batch.add(len(draw_order) * 4, GL_QUADS, MapGroup(ShaderGroup(map_shader, TextureGroup(dungeon_tex, pyglet.graphics.OrderedGroup(0)))),
    ('v2f/static', vertices),
    ('t3f/static', tex_coords),
    ('c3B/dynamic', prepare_lighting()),
)

def update_lighting():
    map_vlist.colors = prepare_lighting()

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

class Player(object):

    def __init__(self):
        control_actor = Actor(100, self.process_control)
        self.actors = (control_actor, )
        self.texture = creatures_tex[HERO_TEX]

    def process_control(self):
        print 'Player acts. Waiting for input...'
        sym, mod = wait_key()

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

        return ACTION_COST

objects = [Player()]

def processor():
    global objects

    actors = []
    for object in objects:
        actors.extend(object.actors)

    time_system = TimeSystem(actors)

    while True:
        time_system.tick()

g_processor = greenlet.greenlet(processor)

@window.event
def on_draw():
    window.clear()
    glPushMatrix()
    glScalef(ZOOM, ZOOM, 1)
    batch.draw()
    draw_tile_objects()
    glPopMatrix()

def wait_key():
    sym, mod = greenlet.getcurrent().parent.switch()
    return sym, mod

g_processor.switch()

@window.event
def on_key_press(sym, mod):
    g_processor.switch(sym, mod)

pyglet.app.run()
