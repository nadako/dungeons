from bisect import insort_right
from collections import defaultdict, deque
import random

from actor import Actor
from components import Blocker
from door import Door
from generator import LayoutGenerator
from level_object import LevelObject, Description
from monster import create_random_monster
from render import Renderable, LayoutRenderable
from temp import light_anim, fountain_anim, library_texes


class Level(object):

    def __init__(self, game, size_x, size_y):
        self.game = game
        self.size_x = size_x
        self.size_y = size_y

        self._objects = defaultdict(list)
        self._actors = deque()

        self._generate_level()

    def _generate_level(self):
        self._layout = LayoutGenerator(self.size_x, self.size_y)
        self._layout.generate()
        self._process_layout()
        self._add_features()
        self._add_monsters()

    def _process_layout(self):
        grid = self._layout.grid
        for x in xrange(grid.size_x):
            for y in xrange(grid.size_y):
                tile = grid[x, y]
                if tile in (LayoutGenerator.TILE_DOOR_CLOSED, LayoutGenerator.TILE_DOOR_OPEN):
                    self.add_object(Door(tile == LayoutGenerator.TILE_DOOR_OPEN), x, y)
                    self.add_object(LevelObject(Description('Floor'), LayoutRenderable(tile)), x, y)
                elif tile == LayoutGenerator.TILE_WALL:
                    wall = LevelObject(Description('Wall'), Blocker(True, True), LayoutRenderable(tile))
                    wall.order = LevelObject.ORDER_WALLS
                    self.add_object(wall, x, y)
                elif tile == LayoutGenerator.TILE_FLOOR:
                    self.add_object(LevelObject(Description('Floor'), LayoutRenderable(tile)), x, y)

    def _add_features(self):
        # TODO: factor this out into feature generator
        for room in self._layout.rooms:
            feature = random.choice([None, 'light', 'fountain', 'library'])
            if feature == 'light':
                coords = random.sample([
                    (room.x + 1, room.y + 1),
                    (room.x + room.grid.size_x - 2, room.y + 1),
                    (room.x + 1, room.y + room.grid.size_y - 2),
                    (room.x + room.grid.size_x - 2, room.y + room.grid.size_y - 2),
                ], random.randint(1, 4))
                for x, y in coords:
                    light = LevelObject(Renderable(light_anim, True), Blocker(blocks_movement=True), Description('Light'))
                    light.order = LevelObject.ORDER_FEATURES
                    self.add_object(light, x, y)
            elif feature == 'fountain':
                fountain = LevelObject(Renderable(fountain_anim, True), Blocker(blocks_movement=True), Description('Fountain'))
                fountain.order = LevelObject.ORDER_FEATURES
                self.add_object(fountain, room.x + room.grid.size_x / 2, room.y + room.grid.size_y / 2)
            elif feature == 'library':
                y = room.y + room.grid.size_y - 1
                for x in xrange(room.x + 1, room.x + room.grid.size_x - 1):
                    if self._layout.grid[x, y] != LayoutGenerator.TILE_WALL:
                        continue
                    if x == room.x + 1 and self._layout.grid[room.x, y - 1] != LayoutGenerator.TILE_WALL:
                        continue
                    if x == room.x + room.grid.size_x - 2 and self._layout.grid[x + 1, y - 1] != LayoutGenerator.TILE_WALL:
                        continue
                    shelf = LevelObject(Renderable(random.choice(library_texes), True), Blocker(False, True), Description('Bookshelf'))
                    shelf.order = LevelObject.ORDER_FEATURES
                    self.add_object(shelf, x, y - 1)

    def _add_monsters(self):
        for room in self._layout.rooms:
            for i in xrange(random.randint(0, 3)):
                x = random.randrange(room.x + 1, room.x + room.grid.size_x - 1)
                y = random.randrange(room.y + 1, room.y + room.grid.size_y - 1)

                if self.blocks_movement(x, y):
                    continue

                monster = create_random_monster()
                self.add_object(monster, x, y)

    def blocks_sight(self, x, y):
        if not self._layout.in_bounds(x, y):
            return True

        for object in self.get_objects_at(x, y):
            if object.has_component(Blocker) and object.blocker.blocks_sight:
                return object

        return False

    def blocks_movement(self, x, y):
        if not self._layout.in_bounds(x, y):
            return True

        for object in self.get_objects_at(x, y):
            if object.has_component(Blocker) and object.blocker.blocks_movement:
                return object

        return False

    def get_objects_at(self, x, y):
        if (x, y) not in self._objects:
            return ()
        return self._objects[x, y]

    def add_object(self, obj, x, y):
        insort_right(self._objects[x, y], obj)
        obj.x = x
        obj.y = y
        obj.level = self

        if obj.has_component(Actor):
            self._actors.append(obj.actor)

    def remove_object(self, obj):
        self._objects[obj.x, obj.y].remove(obj)
        obj.x = None
        obj.y = None
        obj.level = None

        if obj.has_component(Actor):
            self._actors.remove(obj.actor)

    def move_object(self, obj, x, y):
        self._objects[obj.x, obj.y].remove(obj)
        insort_right(self._objects[x, y], obj)
        obj.x = x
        obj.y = y

    def tick(self):
        if self._actors:
            actor = self._actors[0]
            self._actors.rotate()
            actor.energy += actor.speed
            while actor.energy > 0:
                action = actor.act()
                actor.energy -= action.cost
                action.do(actor.owner)

    def get_wall_transition(self, x, y):
        return self._layout.get_wall_transition(x, y)
