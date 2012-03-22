from description import Description
from entity import Component, Entity
from level import Blocker
from position import Position
from render import Renderable
from temp import open_door_tex, closed_door_tex


class Door(Component):

    def __init__(self, is_open=False):
        self.is_open = is_open

    def get_name(self):
        return 'Open door' if self.is_open else 'Closed door'


def get_door_tex(is_open):
    return open_door_tex if is_open else closed_door_tex


def door_bump(blocker, who):
    door = blocker.owner
    door_component = door.get(Door)
    door_component.is_open = not door_component.is_open

    blocker.blocks_sight = not door_component.is_open
    blocker.blocks_movement = not door_component.is_open

    door.get(Renderable).image = get_door_tex(door_component.is_open)
    door.get(Description).name = door_component.get_name()

    who.event('door_open', door)


def create_door(x=0, y=0, is_open=False):
    door_component = Door(is_open)
    return Entity(
        door_component,
        Position(x, y, Position.ORDER_FEATURES),
        Renderable(get_door_tex(is_open)),
        Blocker(not is_open, not is_open, door_bump),
        Description(door_component.get_name())
    )
