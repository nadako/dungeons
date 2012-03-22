import pyglet

from description import Description
from entity import Component, Entity
from fov import FOV
from level import Blocker
from position import Position
from temp import open_door_tex, closed_door_tex


class Door(Component):

    def __init__(self, is_open=False):
        self.is_open = is_open

    def get_name(self):
        return 'Open door' if self.is_open else 'Closed door'


class DoorRenderable(Component):

    COMPONENT_NAME = 'renderable'

    def __init__(self):
        self.open_sprite = pyglet.sprite.Sprite(open_door_tex)
        self.closed_sprite = pyglet.sprite.Sprite(closed_door_tex)
        self.save_memento = True

    @property
    def sprite(self):
        return self.owner.get(Door).is_open and self.open_sprite or self.closed_sprite

    def get_memento_sprite(self):
        return self.sprite


def door_bump(blocker, who):
    door = blocker.owner
    door_component = door.get(Door)
    door_component.is_open = not door_component.is_open

    blocker.blocks_sight = not door_component.is_open
    blocker.blocks_movement = not door_component.is_open

    door.get(Description).name = door_component.get_name()

    who.event('door_open', door)

    # TODO: this doesnt belong here, fov updates should go when generic blocker changes blocks_sight
    if who.has(FOV):
        who.get(FOV).update_light()


def create_door(x=0, y=0, is_open=False):
    door_component = Door(is_open)
    return Entity(
        door_component,
        Position(x, y, Position.ORDER_FEATURES),
        DoorRenderable(),
        Blocker(not is_open, not is_open, door_bump),
        Description(door_component.get_name())
    )
