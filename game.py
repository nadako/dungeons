import functools
import random

import greenlet
import pyglet
from pyglet.window import key
from pyglet import gl

from command import Command
from monster import InFOV
from player import create_player
from level import Level
from components import Renderable
from light import LightOverlay
from message import MessageLog, LastMessagesView
from render import Animation
from temp import get_wall_tex, floor_tex
from generator import LayoutGenerator


class GameExit(Exception):
    pass


class Game(object):

    ZOOM = 3
    DUNGEON_SIZE_X = 100
    DUNGEON_SIZE_Y = 100

    def __init__(self, window):
        self.window = window
        self._g_root = greenlet.getcurrent()
        self._g_mainloop = greenlet.greenlet(self.gameloop)
        self._fpsdisplay = pyglet.clock.ClockDisplay()

    def _render_level(self):
        self._level_sprites = {}
        for x in xrange(self.level.layout.grid.size_x):
            for y in xrange(self.level.layout.grid.size_y):
                tile = self.level.layout.grid[x, y]
                if tile == LayoutGenerator.TILE_WALL:
                    tex = get_wall_tex(self.level.layout.get_wall_transition(x, y))
                    sprite = pyglet.sprite.Sprite(tex, x * 8, y * 8)
                elif tile == LayoutGenerator.TILE_FLOOR:
                    sprite = pyglet.sprite.Sprite(floor_tex, x * 8, y * 8)
                else:
                    sprite = None
                self._level_sprites[x, y] = sprite

    def gameloop(self):
        self._text_overlay_batch = pyglet.graphics.Batch()

        self._message_log = MessageLog()
        self._last_messages_view = LastMessagesView(self._message_log, self.window.width, self.window.height)

        layout = LayoutGenerator(self.DUNGEON_SIZE_X, self.DUNGEON_SIZE_Y)
        layout.generate()
        self.level = Level(self, layout)

        self._render_level()
        self._light_overlay = LightOverlay(self.level.layout.grid.size_x, self.level.layout.grid.size_y)
        self._memento = {}

        self.player = create_player()
        room = random.choice(self.level.layout.rooms)
        self.level.add_object(self.player, room.x + room.grid.size_x / 2, room.y + room.grid.size_y / 2)
        self.player.fov.updated_callback = self._on_player_fov_update
        self.player.fov.update_light()

        self._player_status = pyglet.text.Label(font_name='eight2empire', anchor_y='bottom')

        while True:
            self._update_player_status()
            self.level.tick()

    def _update_player_status(self):
        fighter = self.player.fighter
        inventory = ', '.join(item.name for item in self.player.inventory.items) or 'nothing'
        text = 'HP: %d/%d, ATK: %d, DEF: %d (INV: %s)' % (fighter.health, fighter.max_health, fighter.attack, fighter.defense, inventory)
        self._player_status.text = text

    def _on_player_fov_update(self, old_lightmap, new_lightmap):
        # update light overlay
        self._light_overlay.update_light(new_lightmap)

        # set in_fov flags
        keys = set(old_lightmap).intersection(new_lightmap)
        for key in keys:
            for obj in self.level.get_objects_at(*key):
                if obj.has_component(InFOV):
                    obj.in_fov.in_fov = key in new_lightmap

    def start(self):
        self.window.push_handlers(self)
        self._g_mainloop.switch()

    def get_command(self):
        return self._g_root.switch()

    def message(self, text, color=(255, 255, 255, 255)):
        if color:
            text = '{color (%d, %d, %d, %d)}%s' % (color + (text,))
        self._message_log.add_message(text)

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glPushMatrix()

        gl.glScalef(self.ZOOM, self.ZOOM, 1)
        gl.glTranslatef(self.window.width / (2 * self.ZOOM) - self.player.x * 8, self.window.height / (2 * self.ZOOM) - self.player.y * 8, 0)

        for x in xrange(self.level.layout.grid.size_x):
            for y in xrange(self.level.layout.grid.size_y):

                if self.player.fov.is_in_fov(x, y):
                    level_sprite = self._level_sprites[x, y]
                    level_sprite.draw()

                    objects_memento = []

                    if (x, y) in self.level.objects and len(self.level.objects[x, y]) > 0:
                        for obj in self.level.objects[x, y]:
                            if obj.has_component(Renderable):
                                gl.glPushMatrix()
                                gl.glTranslatef(x * 8, y * 8, 0)
                                obj.renderable.sprite.draw()
                                gl.glPopMatrix()
                                if obj.renderable.save_memento:
                                    objects_memento.append(obj.renderable.get_memento_sprite())

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

        gl.glPushMatrix()
        gl.glTranslatef(self.window.width / 2 - self.player.x * 8 * self.ZOOM, self.window.height / 2 - self.player.y * 8 * self.ZOOM, 0)
        self._text_overlay_batch.draw()
        gl.glPopMatrix()

        self._last_messages_view.draw()
        self._player_status.draw()
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
        elif sym == key.G:
            command = Command(Command.PICKUP, None)

        if command is not None:
            self._g_mainloop.switch(command)


    def animate_damage(self, x, y, dmg):
        # hacky hack
        x = (x * 8 + 4) * self.ZOOM
        start_y = (y * 8 + 4) * self.ZOOM

        label = pyglet.text.Label('-' + str(dmg), font_name='eight2empire', color=(255, 0, 0, 255),
                                  x=x, y=start_y, anchor_x='center', anchor_y='center',
                                  batch=self._text_overlay_batch)

        def update_label(animation):
            label.y = start_y + 12 * self.ZOOM * animation.anim_time
            alpha = int((1.0 - animation.anim_time / animation.duration) * 255)
            label.color = (255, 0, 0, alpha)

        anim = Animation(1)
        anim.update = functools.partial(update_label, anim)
        anim.finish = label.delete
