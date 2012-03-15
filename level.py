from bisect import insort_right
from collections import defaultdict, deque
import random

from actor import Actor
from blocker import Blocker
from description import Description
from door import Door
from entity import Entity
from generator import LayoutGenerator
from monster import create_random_monster
from position import Position
from render import Renderable, LayoutRenderable
from temp import light_anim, fountain_anim, library_texes


class BOUNDS(object):
    def __repr__(self):
        return '<BOUNDS>'
    def __nonzero__(self):
        return True
BOUNDS = BOUNDS()


class Level(object):

    def __init__(self, game, size_x, size_y):
        self.game = game
        self.size_x = size_x
        self.size_y = size_y

        self._entities = set()
        self._positions = defaultdict(list)
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
                    self.add_entity(Door(x, y, tile == LayoutGenerator.TILE_DOOR_OPEN))
                    self.add_entity(Entity(Description('Floor'), LayoutRenderable(tile), Position(x, y)))
                elif tile == LayoutGenerator.TILE_WALL:
                    self.add_entity(Entity(Description('Wall'), Blocker(True, True), LayoutRenderable(tile), Position(x, y, Position.ORDER_WALLS)))
                elif tile == LayoutGenerator.TILE_FLOOR:
                    self.add_entity(Entity(Description('Floor'), LayoutRenderable(tile), Position(x, y)))

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
                    self.add_entity(Entity(
                        Renderable(light_anim, True),
                        Blocker(blocks_movement=True),
                        Description('Light'),
                        Position(x, y, Position.ORDER_FEATURES)
                    ))
            elif feature == 'fountain':
                self.add_entity(Entity(
                    Renderable(fountain_anim, True),
                    Blocker(blocks_movement=True),
                    Description('Fountain'),
                    Position(room.x + room.grid.size_x / 2, room.y + room.grid.size_y / 2, Position.ORDER_FEATURES)
                ))
            elif feature == 'library':
                y = room.y + room.grid.size_y - 1
                for x in xrange(room.x + 1, room.x + room.grid.size_x - 1):
                    if self._layout.grid[x, y] != LayoutGenerator.TILE_WALL:
                        continue
                    if x == room.x + 1 and self._layout.grid[room.x, y - 1] != LayoutGenerator.TILE_WALL:
                        continue
                    if x == room.x + room.grid.size_x - 2 and self._layout.grid[x + 1, y - 1] != LayoutGenerator.TILE_WALL:
                        continue
                    self.add_entity(Entity(
                        Renderable(random.choice(library_texes), True),
                        Blocker(blocks_movement=True),
                        Description('Bookshelf'),
                        Position(x, y - 1, Position.ORDER_FEATURES)
                    ))

    def _add_monsters(self):
        for room in self._layout.rooms:
            for i in xrange(random.randint(0, 3)):
                x = random.randrange(room.x + 1, room.x + room.grid.size_x - 1)
                y = random.randrange(room.y + 1, room.y + room.grid.size_y - 1)
                if not self.get_movement_blocker(x, y):
                    self.add_entity(create_random_monster(x, y))

    def get_sight_blocker(self, x, y):
        if not self._layout.in_bounds(x, y):
            return BOUNDS

        for entity in self.get_entities_at(x, y):
            blocker = entity.get(Blocker)
            if blocker and blocker.blocks_sight:
                return blocker

        return None

    def get_movement_blocker(self, x, y):
        if not self._layout.in_bounds(x, y):
            return BOUNDS

        for entity in self.get_entities_at(x, y):
            blocker = entity.get(Blocker)
            if blocker and blocker.blocks_movement:
                return blocker

        return None

    def get_entities_at(self, x, y):
        if (x, y) not in self._positions:
            return ()
        return [entity for order, entity in self._positions[x, y]]

    def add_entity(self, entity):
        entity.level = self
        self._entities.add(entity)

        pos = entity.get(Position)
        if pos:
            insort_right(self._positions[pos.x, pos.y], (pos.order, entity))

        actor = entity.get(Actor)
        if actor:
            self._actors.append(actor)

    def remove_entity(self, entity):
        self._entities.remove(entity)
        entity.level = None

        pos = entity.get(Position)
        if pos:
            self._positions[pos.x, pos.y].remove((pos.order, entity))

        actor = entity.get(Actor)
        if actor:
            self._actors.remove(actor)

    def move_entity(self, entity, x, y):
        pos = entity.get(Position)
        self._positions[pos.x, pos.y].remove((pos.order, entity))
        insort_right(self._positions[x, y], (pos.order, entity))
        pos.x = x
        pos.y = y

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
