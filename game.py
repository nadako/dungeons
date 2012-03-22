import functools
import random

import greenlet
import pyglet
from pyglet.window import key
from pyglet import gl

from command import Command
from description import get_name
from fight import Fighter
from fov import FOV
from health import Health
from inventory import Inventory
from item import Item
from monster import InFOV
from player import create_player
from level import Level
from light import LightOverlay
from message import MessageLog, LastMessagesView, MessageLogger
from render import Animation, TextureGroup, Renderable, LayoutRenderable, Camera
from temp import get_wall_tex, floor_tex, dungeon_tex
from generator import LayoutGenerator


class GameState(object):

    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass


class Game(object):

    def __init__(self):
        self.window = pyglet.window.Window(1024, 768, 'Dungeon')
        self._states = []

    def change_state(self, state):
        if self._states:
            prev_state = self._states.pop()
            prev_state.exit()
        self._states.append(state)
        state.enter()

    def push_state(self, state):
        if self._states:
            self._states[-1].pause()
        self._states.append(state)
        state.enter()

    def pop_state(self):
        if self._states:
            prev_state = self._states.pop()
            prev_state.exit()
        if self._states:
            self._states[-1].resume()

    def run(self):
        self.push_state(MainMenuState(self))
        pyglet.app.run()

    def quit(self):
        while self._states:
            state = self._states.pop()
            state.exit()
        pyglet.app.exit()


class MainMenuState(GameState):

    def enter(self):
        text = 'ENTER - play, ESC - quit'
        x = self.game.window.width / 2
        y = self.game.window.height / 2
        self.label = pyglet.text.Label(text, x=x, y=y, anchor_x='center', anchor_y='center')
        self.game.window.push_handlers(self)

    def exit(self):
        self.game.window.remove_handlers(self)
        self.label.delete()

    def on_draw(self):
        self.label.draw()

    def on_key_press(self, sym, mod):
        if sym == key.ESCAPE:
            self.game.quit()
        elif sym == key.ENTER:
            self.game.change_state(PlayLevelState(self.game))
        return pyglet.event.EVENT_HANDLED


class PlayLevelState(GameState):

    DUNGEON_SIZE_X = 100
    DUNGEON_SIZE_Y = 100
    ZOOM = 3

    def enter(self):
        self._g_root = greenlet.getcurrent()
        self._g_loop = greenlet.greenlet(self._loop)

        self.level = Level(self, self.DUNGEON_SIZE_X, self.DUNGEON_SIZE_Y)
        self._render_level()
        self._light_overlay = LightOverlay(self.level.size_x, self.level.size_y)
        self._text_overlay_batch = pyglet.graphics.Batch()
        self._message_log = MessageLog()
        self._last_messages_view = LastMessagesView(self._message_log, self.game.window.width, self.game.window.height)

        room = random.choice(self.level._layout.rooms) # TODO: refactor this to stairs up/down
        self.player = create_player(room.x + room.grid.size_x / 2, room.y + room.grid.size_y / 2)
        self.player.add(MessageLogger(self._message_log))
        self.player.listen('fov_updated', self._on_player_fov_update)
        self.level.add_entity(self.player)
        self.player.get(FOV).update_light()

        self._player_status = pyglet.text.Label(font_name='eight2empire', anchor_y='bottom')
        self._camera = Camera(self.game.window, self.ZOOM, self.player)

        self.game.window.push_handlers(self)

        self._g_loop.switch()

    def exit(self):
        self.game.window.remove_handlers(self)
        self._level_vlist.delete()
        self._light_overlay.delete()
        self._last_messages_view.delete()

    def on_key_press(self, sym, mod):
        if sym == key.ESCAPE:
            self.game.quit()
            return pyglet.event.EVENT_HANDLED

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
        elif sym == key.D:
            command = Command(Command.DROP, None)

        if command is not None:
            self._g_loop.switch(command)

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

        self.level.render_system.draw()

    def _draw_hud(self):
        self._last_messages_view.draw()
        self._player_status.draw()

    def _render_level(self):
        vertices = []
        tex_coords = []

        for x in xrange(self.level.size_x):
            for y in xrange(self.level.size_y):
                x1 = x * 8
                x2 = x1 + 8
                y1 = y * 8
                y2 = y1 + 8

                for entity in self.level.position_system.get_entities_at(x, y):
                    renderable = entity.get(LayoutRenderable)
                    if renderable:
                        tile = renderable.tile
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

    def _update_player_status(self):
        item_names = []
        for item in self.player.get(Inventory).items:
            name = get_name(item)
            item_component = item.get(Item)
            if item_component.quantity > 1:
                name += ' (%d)' % item_component.quantity
            item_names.append(name)
        inventory = ', '.join(item_names) or 'nothing'
        fighter = self.player.get(Fighter)
        health = self.player.get(Health)
        text = 'HP: %d/%d, ATK: %d, DEF: %d (INV: %s)' % (health.health, health.max_health, fighter.attack, fighter.defense, inventory)
        self._player_status.text = text

    def _on_player_fov_update(self, player, old_lightmap, new_lightmap):
        # update light overlay
        self._light_overlay.update_light(new_lightmap, {})

        # set in_fov flags
        keys = set(old_lightmap).intersection(new_lightmap)
        for key in keys:
            for entity in self.level.position_system.get_entities_at(*key):
                infov = entity.get(InFOV)
                if infov:
                    infov.in_fov = key in new_lightmap

    def _loop(self):
        while True:
            self._update_player_status()
            self.level.tick()

    def get_command(self):
        command = self._g_root.switch()
        self._message_log.mark_as_seen()
        return command

    def animate_damage(self, x, y, dmg):
        # hacky hack
        x = (x * 8 + random.randint(2, 6)) * self.ZOOM
        start_y = (y * 8 + random.randint(0, 4)) * self.ZOOM

        label = pyglet.text.Label('-' + str(dmg), font_name='eight2empire', color=(255, 0, 0, 255),
            x=x, y=start_y, anchor_x='center', anchor_y='bottom',
            batch=self._text_overlay_batch)

        def update_label(animation):
            label.y = start_y + 12 * self.ZOOM * animation.anim_time
            alpha = int((1.0 - animation.anim_time / animation.duration) * 255)
            label.color = (255, 0, 0, alpha)

        anim = Animation(0.5)
        anim.update = functools.partial(update_label, anim)
        anim.finish = label.delete
