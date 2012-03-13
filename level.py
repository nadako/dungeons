from bisect import insort_right
from collections import defaultdict, deque

from components import Blocker, Actor
from door import Door
from level_generator import TILE_EMPTY, TILE_WALL, TILE_DOOR_CLOSED, TILE_DOOR_OPEN, TILE_FLOOR


class Level(object):

    def __init__(self, game, size_x, size_y):
        self.game = game
        self.size_x = size_x
        self.size_y = size_y
        self.grid = [TILE_EMPTY for _ in xrange(size_x * size_y)]
        self.rooms = []
        self.objects = defaultdict(list)
        self.actors = deque()

    def blocks_sight(self, x, y):
        if not self.in_bounds(x, y):
            return True

        if self.get_tile(x, y) == TILE_WALL:
            return True

        if (x, y) in self.objects:
            for object in self.objects[x, y]:
                if object.has_component(Blocker) and object.blocker.blocks_sight:
                    return object

        return False

    def blocks_movement(self, x, y):
        if not self.in_bounds(x, y):
            return True

        if self.get_tile(x, y) == TILE_WALL:
            return True

        if (x, y) in self.objects:
            for object in self.objects[x, y]:
                if object.has_component(Blocker) and object.blocker.blocks_movement:
                    return object

        return False

    def get_tile(self, x, y):
        return self.grid[y * self.size_x + x]

    def set_tile(self, x, y, tile):
        if tile in (TILE_DOOR_CLOSED, TILE_DOOR_OPEN):
            is_open = (tile == TILE_DOOR_OPEN)
            tile = TILE_FLOOR
            self.add_object(Door(is_open), x, y)

        self.grid[y * self.size_x + x] = tile

    def in_bounds(self, x, y):
        return x >= 0 and x < self.size_x and y >= 0 and y < self.size_y

    def add_object(self, obj, x, y):
        insort_right(self.objects[x, y], obj)
        obj.x = x
        obj.y = y
        obj.level = self

        if obj.has_component(Actor):
            self.actors.append(obj.actor)

    def remove_object(self, obj):
        self.objects[obj.x, obj.y].remove(obj)
        obj.x = None
        obj.y = None
        obj.level = None

        if obj.has_component(Actor):
            self.actors.remove(obj.actor)

    def move_object(self, obj, x, y):
        self.objects[obj.x, obj.y].remove(obj)
        insort_right(self.objects[x, y], obj)
        obj.x = x
        obj.y = y

    def tick(self):
        if self.actors:
            actor = self.actors[0]
            self.actors.rotate()
            actor.energy += actor.speed
            while actor.energy > 0:
                actor.energy -= actor.act()
