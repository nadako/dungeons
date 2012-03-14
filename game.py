import functools
import random

import greenlet
import pyglet
from pyglet.window import key
from pyglet import gl

from camera import Camera
from command import Command
from monster import InFOV
from player import create_player
from level import Level
from components import Renderable, LayoutRenderable
from light import LightOverlay
from message import MessageLog, LastMessagesView
from render import Animation, TextureGroup
from temp import get_wall_tex, floor_tex, dungeon_tex
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

    def _render_level(self):
        vertices = []
        tex_coords = []

        for x in xrange(self.level.size_x):
            for y in xrange(self.level.size_y):
                x1 = x * 8
                x2 = x1 + 8
                y1 = y * 8
                y2 = y1 + 8

                for object in self.level.get_objects_at(x, y):
                    if object.has_component(LayoutRenderable):
                        tile = object.layout_renderable.tile
                        break
                else:
                    continue

                # always add floor, because we wanna draw walls above floor
                vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
                tex_coords.extend(floor_tex.tex_coords)

                if tile == LayoutGenerator.TILE_WALL:
                    # if we got wall, draw it above floor
                    tex = get_wall_tex(self.level.get_wall_transition(x, y))
                    vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
                    tex_coords.extend(tex.tex_coords)

        group = TextureGroup(dungeon_tex)
        self._level_batch = pyglet.graphics.Batch()
        self._level_vlist = self._level_batch.add(len(vertices) / 2, pyglet.gl.GL_QUADS, group,
            ('v2i/static', vertices),
            ('t3f/statc', tex_coords),
        )

    def gameloop(self):
        self._text_overlay_batch = pyglet.graphics.Batch()

        self._message_log = MessageLog()
        self._last_messages_view = LastMessagesView(self._message_log, self.window.width, self.window.height)

        self.level = Level(self, self.DUNGEON_SIZE_X, self.DUNGEON_SIZE_Y)

        self._render_level()
        self._light_overlay = LightOverlay(self.level.size_x, self.level.size_y)
        self._memento = {}

        self.player = create_player()
        room = random.choice(self.level._layout.rooms) # TODO: refactor this to stairs up/down
        self.level.add_object(self.player, room.x + room.grid.size_x / 2, room.y + room.grid.size_y / 2)
        self.player.fov.updated_callback = self._on_player_fov_update
        self.player.fov.update_light()

        self._player_status = pyglet.text.Label(font_name='eight2empire', anchor_y='bottom')
        self._camera = Camera(self.window, self.ZOOM, self.player)

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
        self._light_overlay.update_light(new_lightmap, self._memento)

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

        with self._camera:
            gl.glPushMatrix()
            gl.glScalef(self.ZOOM, self.ZOOM, 1)
            self._draw_layout_and_objects()

            # draw FOV overlay, hiding unexplored level tiles and adding some lighting effect
            pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
            pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
            self._light_overlay.draw()
            gl.glPopMatrix()

            # draw unscaledtext overlays (like dmg digits and so on)
            self._text_overlay_batch.draw()

        self._draw_hud()

    def _draw_layout_and_objects(self):
        # draw level layout
        self._level_batch.draw()

        # prepare a collection of remembered objects to draw (we will remove parts that are currently in FOV)
        memento_to_draw = self._memento.copy()

        for key in self.player.fov.lightmap:
            # remove from memento to draw as we're going to update it and draw current contents in this loop
            memento_to_draw.pop(key, None)

            # draw all objects in this tile and remember objects saveable in memento
            x, y = key
            objects_memento = []
            for obj in self.level.get_objects_at(*key):
                if obj.has_component(Renderable):
                    gl.glPushMatrix()
                    gl.glTranslatef(x * 8, y * 8, 0)
                    obj.renderable.sprite.draw()
                    gl.glPopMatrix()
                    if obj.renderable.save_memento:
                        objects_memento.append(obj.renderable.get_memento_sprite())
            self._memento[key] = objects_memento

        # draw remembered objects outside of FOV
        for key, sprites in memento_to_draw.items():
            x, y = key
            for sprite in sprites:
                gl.glPushMatrix()
                gl.glTranslatef(x * 8, y * 8, 0)
                sprite.draw()
                gl.glPopMatrix()


    def _draw_hud(self):
        self._last_messages_view.draw()
        self._player_status.draw()

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
                                  x=x, y=start_y, anchor_x='center', anchor_y='bottom',
                                  batch=self._text_overlay_batch)

        def update_label(animation):
            label.y = start_y + 12 * self.ZOOM * animation.anim_time
            alpha = int((1.0 - animation.anim_time / animation.duration) * 255)
            label.color = (255, 0, 0, alpha)

        anim = Animation(1)
        anim.update = functools.partial(update_label, anim)
        anim.finish = label.delete
