import pyglet

from description import Description
from entity import Component, Entity
from fov import FOV
from level import Blocker
from player import is_player
from position import Position
from temp import open_door_tex, closed_door_tex


class DoorRenderable(Component):

    COMPONENT_NAME = 'renderable'

    def __init__(self):
        self.open_sprite = pyglet.sprite.Sprite(open_door_tex)
        self.closed_sprite = pyglet.sprite.Sprite(closed_door_tex)
        self.save_memento = True

    @property
    def sprite(self):
        return self.owner.is_open and self.open_sprite or self.closed_sprite

    def get_memento_sprite(self):
        return self.sprite


class Door(Entity):

    def __init__(self, x=0, y=0, is_open=False):
        self.is_open = is_open
        super(Door, self).__init__(
            Position(x, y, Position.ORDER_FEATURES),
            DoorRenderable(),
            Blocker(not is_open, not is_open, self.on_bump),
            Description(self.get_name())
        )

    def get_name(self):
        return 'Open door' if self.is_open else 'Closed door'

    def on_bump(self, blocker, who):
        self.is_open = not self.is_open

        if is_player(who):
            who.level.game.message('You open the door')

        blocker.blocks_sight = not self.is_open
        blocker.blocks_movement = not self.is_open

        self.get(Description).name = self.get_name()

        # TODO: this doesnt belong here, fov updates should go when generic blocker changes blocks_sight
        if who.has(FOV):
            who.get(FOV).update_light()
