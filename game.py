from collections import deque
import random

import greenlet
import pyglet
from pyglet.window import key
from pyglet import gl

from level import Level, LevelObject, Actor, Movement, Renderable, FOV, Blocker, Player
from level_generator import LevelGenerator, TILE_EMPTY, TILE_WALL, TILE_FLOOR
from temp import monster_texes, dungeon_tex, wall_tex_row, floor_tex, player_tex, library_texes, light_anim, fountain_anim

from data.eight2empire import WALL_TRANSITION_TILES # load this dynamically, not import as python module


class GameExit(Exception):
    pass


class Game(object):

    EVT_KEY_PRESS = 'key-press'
    DUNGEON_SIZE_X = 100
    DUNGEON_SIZE_Y = 100

    def __init__(self, window):
        self.window = window
        self._g_root = greenlet.getcurrent()
        self._g_mainloop = greenlet.greenlet(self.gameloop)
        self._waiting_event = None

    def _add_features(self):
        # TODO: factor this out into feature generator
        for room in self.level.rooms:
            feature = random.choice([None, 'light', 'fountain', 'library'])
            if feature == 'light':
                coords = random.sample([
                    (room.x + 1, room.y + 1),
                    (room.x + room.size_x - 2, room.y + 1),
                    (room.x + 1, room.y + room.size_y - 2),
                    (room.x + room.size_x - 2, room.y + room.size_y - 2),
                ], random.randint(1, 4))
                for x, y in coords:
                    light = LevelObject(Renderable(light_anim, True), Blocker(blocks_movement=True))
                    self.level.add_object(light, x, y)
            elif feature == 'fountain':
                fountain = LevelObject(Renderable(fountain_anim, True), Blocker(blocks_movement=True))
                self.level.add_object(fountain, room.x + room.size_x / 2, room.y + room.size_y / 2)
            elif feature == 'library':
                y = room.y + room.size_y - 1
                for x in xrange(room.x + 1, room.x + room.size_x - 1):
                    if self.level.get_tile(x, y) != TILE_WALL:
                        continue
                    if x == room.x + 1 and self.level.get_tile(room.x, y - 1) != TILE_WALL:
                        continue
                    if x == room.x + room.size_x - 2 and self.level.get_tile(x + 1, y - 1) != TILE_WALL:
                        continue
                    shelf = LevelObject(Renderable(random.choice(library_texes), True), Blocker(False, True))
                    self.level.add_object(shelf, x, y - 1)

    def _add_monsters(self):
        for room in self.level.rooms:
            for i in xrange(random.randint(0, 3)):
                x = random.randrange(room.x + 1, room.x + room.size_x - 1)
                y = random.randrange(room.y + 1, room.y + room.size_y - 1)

                if (x, y) in self.level.objects and self.level.objects[x, y]:
                    continue

                monster = LevelObject(Actor(100, monster_act), Movement(), Renderable(random.choice(monster_texes)), Blocker(blocks_movement=True))
                self.level.add_object(monster, x, y)

    def _render_level(self):
        self._level_sprites = {}
        for y in xrange(self.level.size_y):
            for x in xrange(self.level.size_x):
                tile = self.level.get_tile(x, y)
                if tile == TILE_WALL:
                    tex = self._get_wall_transition_tile(x, y)
                    sprite = pyglet.sprite.Sprite(tex, x * 8, y * 8)
                elif tile == TILE_FLOOR:
                    sprite = pyglet.sprite.Sprite(floor_tex, x * 8, y * 8)
                else:
                    sprite = None
                self._level_sprites[x, y] = sprite

    def _is_wall(self, x, y):
        if not self.level.in_bounds(x, y):
            return True
        return self.level.get_tile(x, y) in (TILE_WALL, TILE_EMPTY)

    def _get_wall_transition_tile(self, x, y):
        n = 1
        e = 2
        s = 4
        w = 8
        nw = 128
        ne = 16
        se = 32
        sw = 64

        v = 0
        if self._is_wall(x, y + 1):
            v |= n
        if self._is_wall(x + 1, y):
            v |= e
        if self._is_wall(x, y - 1):
            v |= s
        if self._is_wall(x - 1, y):
            v |= w
        if self._is_wall(x - 1, y + 1):
            v |= nw
        if self._is_wall(x + 1, y + 1):
            v |= ne
        if self._is_wall(x - 1, y - 1):
            v |= sw
        if self._is_wall(x + 1, y - 1):
            v |= se

        if v not in WALL_TRANSITION_TILES:
            v &= 15

        return dungeon_tex[wall_tex_row, WALL_TRANSITION_TILES[v]]

    def gameloop(self):
        self._message_log = deque(maxlen=5)
        self._messages_layout = pyglet.text.layout.TextLayout(pyglet.text.document.UnformattedDocument(), width=self.window.width, multiline=True)
        self._messages_layout.anchor_y = 'top'
        self._messages_layout.y = self.window.height

        self.level = Level(self, self.DUNGEON_SIZE_X, self.DUNGEON_SIZE_Y)
        generator = LevelGenerator(self.level)
        generator.generate()

        self._render_level()
        self._create_light_overlay()

        self._add_features()
        self._add_monsters()

        self.player = LevelObject(Actor(100, player_act), FOV(10), Movement(), Renderable(player_tex), Blocker(blocks_movement=True), Player())
        self.player.order = 1
        room = random.choice(self.level.rooms)
        self.level.add_object(self.player, room.x + room.size_x / 2, room.y + room.size_y / 2)
        self.player.fov.on_fov_updated = self._on_player_fov_updated
        self.player.fov.update_light()

        self._memento = {}

        self.zoom = 3

        while True:
            self.level.tick()

    def start(self):
        self.window.push_handlers(self)
        self._switch_to_gameloop()

    def wait_key_press(self):
        return self._g_root.switch(Game.EVT_KEY_PRESS)

    def message(self, text, color=(255, 255, 255, 255)):
        if color:
            text = '{color (%d, %d, %d, %d)}%s' % (color + (text,))
        self._message_log.append(text)
        self._messages_layout.document = pyglet.text.decode_attributed('{font_name "eight2empire"}' + '{}\n'.join(self._message_log))

    def _switch_to_gameloop(self, *data):
        self._waiting_event = self._g_mainloop.switch(*data)

    def _create_light_overlay(self):
        vertices = []
        colors = []
        for tile_y in xrange(self.level.size_y):
            for tile_x in xrange(self.level.size_x):
                x1 = tile_x * 8
                x2 = (tile_x + 1) * 8
                y1 = tile_y * 8
                y2 = (tile_y + 1) * 8
                c = (0, 0, 0, 255)
                vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
                colors.extend((c * 4))

        self._light_vlist = pyglet.graphics.vertex_list(self.level.size_x * self.level.size_y * 4,
            ('v2i', vertices),
            ('c4B', colors)
        )

    def _on_player_fov_updated(self):
        lightmap = self.player.fov.lightmap

        colors = []
        for tile_y in xrange(self.level.size_y):
            for tile_x in xrange(self.level.size_x):
                intensity = lightmap.get((tile_x, tile_y), 0)
                v = int((1 - (0.3 + intensity * 0.7)) * 255)
                c = (0, 0, 0, v)
                colors.extend((c * 4))

        self._light_vlist.colors = colors


    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glPushMatrix()

        gl.glScalef(self.zoom, self.zoom, 1)
        gl.glTranslatef(self.window.width / (2 * self.zoom) - self.player.x * 8, self.window.height / (2 * self.zoom) - self.player.y * 8, 0)

        for x in xrange(self.level.size_x):
            for y in xrange(self.level.size_y):

                if self.player.fov.is_in_fov(x, y):
                    level_sprite = self._level_sprites[x, y]
                    level_sprite.draw()

                    renderable = None
                    objects_memento = []

                    if (x, y) in self.level.objects and len(self.level.objects[x, y]) > 0:
                        for obj in self.level.objects[x, y]:
                            if hasattr(obj, Renderable.component_name):
                                renderable = obj.renderable
                                break

                    if renderable is not None:
                        gl.glPushMatrix()
                        gl.glTranslatef(x * 8, y * 8, 0)
                        renderable.sprite.draw()
                        gl.glPopMatrix()
                        if renderable.save_memento:
                            objects_memento.append(renderable.get_memento_sprite())

                    self._memento[x, y] = (level_sprite, objects_memento)

                elif (x, y) in self._memento:
                    level_sprite, object_sprites = self._memento[x, y]
                    level_sprite.draw()

                    for sprite in object_sprites:
                        gl.glPushMatrix()
                        gl.glTranslatef(x * 8, y * 8, 0)
                        sprite.draw()
                        gl.glPopMatrix()

        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self._light_vlist.draw(pyglet.gl.GL_QUADS)

        gl.glPopMatrix()

        self._messages_layout.draw()


    def on_key_press(self, sym, mod):
        if self._waiting_event == Game.EVT_KEY_PRESS:
            self._switch_to_gameloop(sym, mod)


def player_act(actor):
    player = actor.owner
    sym, mod = player.level.game.wait_key_press()
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
    return 100


def monster_act(actor):
    dx = random.randint(-1, 1)
    dy = random.randint(-1, 1)
    actor.owner.movement.move(dx, dy)
    return 100
