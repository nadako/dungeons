import random

from actor import Actor, ActorSystem
from blocker import Blocker
from description import Description
from door import create_door
from entity import Entity
from fov import FOV
from generator import LayoutGenerator
from health import Health
from item import Item
from monster import create_random_monster
from position import Position, PositionSystem
from render import Renderable, LayoutRenderable, RenderSystem
from temp import light_anim, fountain_anim, library_texes, gold_texes


class BOUNDS(object):
    def __repr__(self):
        return '<BOUNDS>'
    def __nonzero__(self):
        return True
BOUNDS = BOUNDS()


class Level(object):

    def __init__(self, game, size_x, size_y):
        self.actor_system = ActorSystem(self)
        self.position_system = PositionSystem()
        self.render_system = RenderSystem()
        self.game = game
        self.size_x = size_x
        self.size_y = size_y

        self._entities = set()

        self._generate_level()

    def _generate_level(self):
        self._layout = LayoutGenerator(self.size_x, self.size_y)
        self._layout.generate()
        self._process_layout()
        self._add_features()
        self._add_monsters()
        self._add_items()

    def _process_layout(self):
        grid = self._layout.grid
        for x in xrange(grid.size_x):
            for y in xrange(grid.size_y):
                tile = grid[x, y]
                if tile in (LayoutGenerator.TILE_DOOR_CLOSED, LayoutGenerator.TILE_DOOR_OPEN):
                    self.add_entity(create_door(x, y, tile == LayoutGenerator.TILE_DOOR_OPEN))
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
                        Renderable(light_anim),
                        Blocker(blocks_movement=True),
                        Description('Light'),
                        Position(x, y, Position.ORDER_FEATURES)
                    ))
            elif feature == 'fountain':
                self.add_entity(Entity(
                    Renderable(fountain_anim),
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
                        Renderable(random.choice(library_texes)),
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

    def _add_items(self):
        for room in self._layout.rooms:
            if random.random() > 0.3:
                continue
            x = random.randrange(room.x + 1, room.x + room.grid.size_x - 1)
            y = random.randrange(room.y + 1, room.y + room.grid.size_y - 1)
            if not self.get_movement_blocker(x, y):
                self.add_entity(Entity(
                    Description('Gold'),
                    Renderable(random.choice(gold_texes)),
                    Position(x, y, order=Position.ORDER_ITEMS),
                    Item('gold', quantity=random.randint(1, 50)),
                ))

    def get_sight_blocker(self, x, y):
        if not self._layout.in_bounds(x, y):
            return BOUNDS

        for entity in self.position_system.get_entities_at(x, y):
            blocker = entity.get(Blocker)
            if blocker and blocker.blocks_sight:
                return blocker

        return None

    def get_movement_blocker(self, x, y):
        if not self._layout.in_bounds(x, y):
            return BOUNDS

        for entity in self.position_system.get_entities_at(x, y):
            blocker = entity.get(Blocker)
            if blocker and blocker.blocks_movement:
                return blocker

        return None

    def add_entity(self, entity):
        entity.level = self
        self._entities.add(entity)

        if entity.has(Position):
            self.position_system.add_entity(entity)

            if entity.has(Health):
                entity.listen('take_damage', self._on_take_damage)

            if entity.has(Blocker):
                entity.listen('blocks_sight_change', self._on_blocks_sight_change)

            if entity.has(Renderable):
                self.render_system.add_entity(entity)

        if entity.has(Actor):
            self.actor_system.add_entity(entity)


    def remove_entity(self, entity):
        self._entities.remove(entity)
        entity.level = None

        if entity.has(Position):
            self.position_system.remove_entity(entity)

            if entity.has(Health):
                entity.unlisten('take_damage', self._on_take_damage)

            if entity.has(Blocker):
                entity.unlisten('blocks_sight_change', self._on_blocks_sight_change)

            if entity.has(Renderable):
                self.render_system.remove_entity(entity)

        if entity.has(Actor):
            self.actor_system.remove_entity(entity)


    def _on_take_damage(self, entity, amount, source):
        pos = entity.get(Position)
        self.game.animate_damage(pos.x, pos.y, amount)

    def _on_blocks_sight_change(self, entity):
        pos = entity.get(Position)
        fov = self.game.player.get(FOV)
        if fov.is_in_fov(pos.x, pos.y):
            fov.update_light()

    def tick(self):
        self.actor_system.update()

    def get_wall_transition(self, x, y):
        return self._layout.get_wall_transition(x, y)
