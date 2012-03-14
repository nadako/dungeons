import pyglet

from components import FOV
from level_object import LevelObject, Component, Description
from level import Blocker
from player import Player
from temp import open_door_tex, closed_door_tex


class DoorRenderable(Component):

    component_name = 'renderable'

    def __init__(self):
        self.open_sprite = pyglet.sprite.Sprite(open_door_tex)
        self.closed_sprite = pyglet.sprite.Sprite(closed_door_tex)
        self.save_memento = True

    @property
    def sprite(self):
        return self.owner.is_open and self.open_sprite or self.closed_sprite

    def get_memento_sprite(self):
        return self.sprite


class Door(LevelObject):

    def __init__(self, is_open):
        self.order = LevelObject.ORDER_FEATURES
        self.is_open = is_open
        super(Door, self).__init__(DoorRenderable(), Blocker(not is_open, not is_open, self.bump), Description(self.get_name()))

    def get_name(self):
        return 'Open door' if self.is_open else 'Closed door'

    def bump(self, blocker, who):
        assert blocker.owner is self
        if who.has_component(Player):
            self.level.game.message('You open the door')
        self.is_open = not self.is_open
        self.blocker.blocks_sight = not self.is_open
        self.blocker.blocks_movement = not self.is_open
        self.description.name = self.get_name()
        if who.has_component(FOV):
            who.fov.update_light()
