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
        self._x = x
        self._y = y
        self._order = order

    x = property(lambda self:self._x)
    y = property(lambda self:self._y)
    order = property(lambda self:self._order)

    def move(self, x, y):
        if x != self._x or y != self._y:
            old_x, old_y = self._x, self._y
            self._x = x
            self._y = y
            self.owner.event('move', old_x, old_y, self._x, self._y)


class Movement(Component):

    COMPONENT_NAME = 'movement'

    def move(self, dx, dy):
        pos = self.owner.get(Position)
        new_x = pos.x + dx
        new_y = pos.y + dy

        blocker = self.owner.level.get_movement_blocker(new_x, new_y)
        if not blocker:
            pos.move(new_x, new_y)
        elif isinstance(blocker, Blocker):
            blocker.bump_function(blocker, self.owner)


class PositionSystem(object):

    def __init__(self):
        self._positions = defaultdict(list)

    def add_entity(self, entity):
        entity.listen('move', self._on_move)
        position = entity.get(Position)
        insort_right(self._positions[position.x, position.y], (position.order, entity))

    def remove_entity(self, entity):
        position = entity.get(Position)
        self._positions[position.x, position.y].remove((position.order, entity))
        entity.unlisten('move', self._on_move)

    def get_entities_at(self, x, y):
        if (x, y) not in self._positions:
            return ()
        return tuple(entity for order, entity in self._positions[x, y])

    def _on_move(self, entity, old_x, old_y, new_x, new_y):
        pos = entity.get(Position)
        self._positions[old_x, old_y].remove((pos.order, entity))
        insort_right(self._positions[new_x, new_y], (pos.order, entity))
