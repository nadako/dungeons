from bisect import insort_right
from collections import defaultdict

from entity import Component
from blocker import Blocker


class Position(Component):

    COMPONENT_NAME = 'position'

    ORDER_FLOOR = 0
    ORDER_WALLS = 10
    ORDER_FEATURES = 20
    ORDER_ITEMS = 30
    ORDER_CREATURES = 40
    ORDER_PLAYER = 50

    def __init__(self, x=0, y=0, order=ORDER_FLOOR):
        self.x = x
        self.y = y
        self.order = order


class PositionSystem(object):

    def __init__(self):
        self._positions = defaultdict(list)

    def add_entity(self, entity):
        position = entity.get(Position)
        insort_right(self._positions[position.x, position.y], (position.order, entity))

    def remove_entity(self, entity):
        position = entity.get(Position)
        self._positions[position.x, position.y].remove((position.order, entity))

    def get_entities_at(self, x, y):
        if (x, y) not in self._positions:
            return ()
        return tuple(entity for order, entity in self._positions[x, y])

    def move_entity(self, entity, x, y):
        position = entity.get(Position)
        self._positions[position.x, position.y].remove((position.order, entity))
        insort_right(self._positions[x, y], (position.order, entity))
        position.x = x
        position.y = y


# TODO: this component is a mess, don't look there
class Movement(Component):

    COMPONENT_NAME = 'movement'

    def move(self, dx, dy):
        pos = self.owner.get(Position)
        new_x = pos.x + dx
        new_y = pos.y + dy

        blocker = self.owner.level.get_movement_blocker(new_x, new_y)
        if not blocker:
            self.owner.level.position_system.move_entity(self.owner, new_x, new_y)

            fov = self.owner.get(FOV)
            if fov:
                fov.update_light()
        elif isinstance(blocker, Blocker):
            blocker.bump_function(blocker, self.owner)


from fov import FOV
