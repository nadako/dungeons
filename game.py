import collections
import random

import greenlet
import pyglet
from pyglet.window import key
from pyglet import gl

from level import Level, LevelObject, Actor, Movement, Renderable, FOV, Blocker, Player, Fighter, Description
from level_generator import LevelGenerator, TILE_EMPTY, TILE_WALL, TILE_FLOOR
from light import LightOverlay
from message import MessageLog, LastMessagesView
from temp import monster_texes, get_wall_tex, floor_tex, player_tex, library_texes, light_anim, fountain_anim


class GameExit(Exception):
    pass


Command = collections.namedtuple('Command', 'name data')
Command.WAIT = 'wait'
Command.MOVE = 'move'


class Game(object):

    DUNGEON_SIZE_X = 100
    DUNGEON_SIZE_Y = 100

    def __init__(self, window):
        self.window = window
        self._g_root = greenlet.getcurrent()
        self._g_mainloop = greenlet.greenlet(self.gameloop)
        self._fpsdisplay = pyglet.clock.ClockDisplay()

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

                monster = LevelObject(Actor(100, monster_act), Movement(), Renderable(random.choice(monster_texes)), Blocker(blocks_movement=True, bump_function=monster_bump), Fighter(2, 1, 0), Description('Goblin'))
                self.level.add_object(monster, x, y)

    def _render_level(self):
        self._level_sprites = {}
        for y in xrange(self.level.size_y):
            for x in xrange(self.level.size_x):
                tile = self.level.get_tile(x, y)
                if tile == TILE_WALL:
                    tex = get_wall_tex(self._get_wall_transition(x, y))
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

    def _get_wall_transition(self, x, y):
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

        return v

    def gameloop(self):
        self._message_log = MessageLog()
        self._last_messages_view = LastMessagesView(self._message_log, self.window.width, self.window.height)

        self.level = Level(self, self.DUNGEON_SIZE_X, self.DUNGEON_SIZE_Y)
        generator = LevelGenerator(self.level)
        generator.generate()

        self._render_level()
        self._light_overlay = LightOverlay(self.level.size_x, self.level.size_y)

        self._add_features()
        self._add_monsters()

        self.player = LevelObject(Actor(100, player_act), FOV(10), Movement(), Renderable(player_tex), Blocker(blocks_movement=True), Player(), Fighter(100, 1, 0))
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
        self._g_mainloop.switch()

    def get_command(self):
        return self._g_root.switch()

    def message(self, text, color=(255, 255, 255, 255)):
        if color:
            text = '{color (%d, %d, %d, %d)}%s' % (color + (text,))
        self._message_log.add_message(text)

    def _on_player_fov_updated(self):
        self._light_overlay.update_light(self.player.fov.lightmap)

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
        self._light_overlay.draw()

        gl.glPopMatrix()

        self._last_messages_view.draw()
        self._fpsdisplay.draw()


    def on_key_press(self, sym, mod):
        command = None

        if sym == key.NUM_8:
            command = Command(Command.MOVE, (0, 1))
        elif sym == key.NUM_2:
            command = Command(Command.MOVE, (0, -1))
        elif sym == key.NUM_4:
            command = Command(Command.MOVE, (-1, 0))
        elif sym == key.NUM_6:
            command = Command(Command.MOVE, (1, 0))
        elif sym == key.NUM_7:
            command = Command(Command.MOVE, (-1, 1))
        elif sym == key.NUM_9:
            command = Command(Command.MOVE, (1, 1))
        elif sym == key.NUM_1:
            command = Command(Command.MOVE, (-1, -1))
        elif sym == key.NUM_3:
            command = Command(Command.MOVE, (1, -1))
        elif sym == key.NUM_5:
            command = Command(Command.WAIT, None)

        if command is not None:
            self._g_mainloop.switch(command)


def player_act(actor):
    player = actor.owner
    command = player.level.game.get_command()
    player.level.game._message_log.mark_as_seen()
    if command.name == Command.MOVE:
        player.movement.move(*command.data)
    return 100


def monster_act(actor):
    dx = random.randint(-1, 1)
    dy = random.randint(-1, 1)
    actor.owner.movement.move(dx, dy)
    return 100


def monster_bump(blocker, who):
    monster = blocker.owner
    if not hasattr(monster, Fighter.component_name):
        return
    if not hasattr(who, Player.component_name) or not hasattr(who, Fighter.component_name):
        return

    who.fighter.do_attack(monster)
