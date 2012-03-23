import greenlet
import pyglet
from pyglet.window import key
from pyglet import gl

from command import Command
from description import get_name
from fight import Fighter
from health import Health
from inventory import Inventory
from item import Item
from level import Level
from message import MessageLog, LastMessagesView


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

    def enter(self):
        self._g_root = greenlet.getcurrent()
        self._g_loop = greenlet.greenlet(self._loop)

        self.message_log = MessageLog()
        self._last_messages_view = LastMessagesView(self.message_log, self.game.window.width, self.game.window.height)

        self.level = Level(self, self.DUNGEON_SIZE_X, self.DUNGEON_SIZE_Y)

        self._player_status = pyglet.text.Label(font_name='eight2empire', anchor_y='bottom')

        self.game.window.push_handlers(self)

        self._g_loop.switch()

    def exit(self):
        self.game.window.remove_handlers(self)
        self.level.render_system.dispose()
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
        self.level.render_system.draw()
        self._draw_hud()

    def _draw_hud(self):
        self._last_messages_view.draw()
        self._player_status.draw()

    def _update_player_status(self):
        item_names = []
        for item in self.level.player.get(Inventory).items:
            name = get_name(item)
            item_component = item.get(Item)
            if item_component.quantity > 1:
                name += ' (%d)' % item_component.quantity
            item_names.append(name)
        inventory = ', '.join(item_names) or 'nothing'
        fighter = self.level.player.get(Fighter)
        health = self.level.player.get(Health)
        text = 'HP: %d/%d, ATK: %d, DEF: %d (INV: %s)' % (health.health, health.max_health, fighter.attack, fighter.defense, inventory)
        self._player_status.text = text

    def _loop(self):
        while True:
            self._update_player_status()
            self.level.tick()

    def get_command(self):
        command = self._g_root.switch()
        self.message_log.mark_as_seen()
        return command
