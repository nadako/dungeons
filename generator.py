import collections
import random

# handy tuple type for storing coordinates, sizes or directions
from dungeon import TileType, Door

_vec = collections.namedtuple('vec', 'x y')

# direction constants, also contain coordinate offset
DIR_N = _vec(0, -1)
DIR_S = _vec(0, 1)
DIR_W = _vec(-1, 0)
DIR_E = _vec(1, 0)

# basic square room generator (see below for info on what's room generator)
def square_room_generator(min_size, max_size):
    size = _vec(random.randint(min_size.x, max_size.x),
                random.randint(min_size.y, max_size.y))

    tiles = []
    for y in xrange(size.y):
        row = []
        for x in xrange(size.x):
            if x == 0 or y == 0 or x == size.x -1 or y == size.y - 1:
                row.append(TileType.WALL)
            else:
                row.append(TileType.FLOOR)
        tiles.append(row)

    return tiles

# list of all generators (used by generator)
# this system provides a way to plug unusual shaped
# room generation in the current system
# a generator is a simple function that receives minimum
# and maximum room size and returns a 2-dimensional square
# grid (all rows are same length) of generated room tiles
room_generators = [
    square_room_generator,
]

class Room(object):
    """
    Room objects are stored in dungeon and represent
    information about currently created rooms
    """

    def __init__(self, tiles):
        self.tiles = tiles
        self.size = _vec(len(tiles[0]), len(tiles))
        self.position = None # position is set by generator later


class DungeonGenerator(object):
    """
    Main dungeon generator class

    Stores tile grid, list of rooms and provides
    functionality to generate random dungeon.
    """

    def __init__(self, grid, max_rooms=100, min_room_size=(3, 3), max_room_size=(12, 12), door_chance=75, door_open_chance=10):
        self.grid = grid
        self.min_room_size = _vec(*min_room_size)
        self.max_room_size = _vec(*max_room_size)
        self.max_rooms = max_rooms
        self.door_chance = door_chance
        self.door_open_chance = door_open_chance
        self.clear()

    def clear(self):
        # clear grid and room list
        self.grid.clear()
        self.rooms = []

    def generate_room(self):
        # choose random generator and use it to create tiles
        # TODO: add chance-based random generator selection
        generator = random.choice(room_generators)
        tiles = generator(self.min_room_size, self.max_room_size)

        # return room object for generated tiles
        return Room(tiles)

    def place_room(self, room, position):
        # set room object position
        room.position = position

        # append room to the list of generated rooms
        self.rooms.append(room)

        # add room tiles to dungeon grid (skipping empty tiles)
        for y in xrange(room.position.y, room.position.y + room.size.y):
            for x in xrange(room.position.x, room.position.x + room.size.x):
                tile = room.tiles[y - room.position.y][x - room.position.x]
                if tile != TileType.EMPTY:
                    self.grid[x, y].type = tile

    def choose_gate(self):
        # choose random room and side
        room = random.choice(self.rooms)
        side = random.choice((DIR_E, DIR_W, DIR_N, DIR_S))

        # prepare list of tiles of chosen side, excluding corners
        if side is DIR_N:
            gates = [_vec(room.position.x + x, room.position.y) for x in xrange(1, room.size.x - 1)]
        elif side is DIR_S:
            gates = [_vec(room.position.x + x, room.position.y + room.size.y - 1) for x in xrange(1, room.size.x - 1)]
        elif side is DIR_W:
            gates = [_vec(room.position.x, room.position.y + y) for y in xrange(1, room.size.y - 1)]
        elif side is DIR_E:
            gates = [_vec(room.position.x + room.size.x - 1, room.position.y + y) for y in xrange(1, room.size.y - 1)]

        # choose random tile from list as a gate
        gate = random.choice(gates)

        # return chosen gate and direction (side)
        return gate, side

    def has_space_for_room(self, room, position):
        xstart = position.x
        xend = xstart + room.size.x
        ystart = position.y
        yend = ystart + room.size.y

        if xstart < 0 or xend > self.grid.size_x or ystart < 0 or yend > self.grid.size_y:
            return False

        for y in xrange(ystart, yend):
            for x in xrange(xstart, xend):
                if room.tiles[y - ystart][x - xstart] == TileType.EMPTY:
                    continue
                elif self.grid[x, y].type != TileType.EMPTY:
                    return False

        return True

    def connect_rooms(self, gate, dir):
        self.grid[gate.x, gate.y].type = TileType.FLOOR
        self.grid[gate.x + dir.x, gate.y + dir.y].type = TileType.FLOOR

        if random.random() * 100 < self.door_chance:
            is_open = random.random() * 100 < self.door_open_chance
            if random.random() < 0.5:
                self.grid[gate.x, gate.y].add_object(Door(is_open))
            else:
                self.grid[gate.x + dir.x, gate.y + dir.y].add_object(Door(is_open))


    def generate(self):
        room = self.generate_room()
        center = _vec((self.grid.size_x - room.size.x) / 2, (self.grid.size_y - room.size.y) / 2)
        self.place_room(room, center)

        for i in xrange(self.grid.size_x * self.grid.size_y * 2):
            # if we generated enough rooms, stop
            if self.max_rooms and len(self.rooms) >= self.max_rooms:
                break

            # generate random room
            room = self.generate_room()

            # choose gate and direction for placing new room
            gate, dir = self.choose_gate()

            # calculate position for new room (add some randomness)
            if dir == DIR_N:
                position = _vec(gate.x - random.randrange(1, room.size.x - 1), gate.y - room.size.y)
            elif dir == DIR_S:
                position = _vec(gate.x - random.randrange(1, room.size.x - 1), gate.y + 1)
            elif dir == DIR_W:
                position = _vec(gate.x - room.size.x, gate.y - random.randrange(1, room.size.y - 1))
            elif dir == DIR_E:
                position = _vec(gate.x + 1, gate.y - random.randrange(1, room.size.y - 1))

            # if there's enough space, place room and connect rooms with hallway
            if self.has_space_for_room(room, position):
                self.place_room(room, position)
                self.connect_rooms(gate, dir)
            else:
                # otherwise, increase attempt count
                i += 1

    def print_dungeon(self):
        print 'size: %dx%d' % (self.grid.size_x, self.grid.size_y)
        print 'rooms: %d / %d' % (len(self.rooms), self.max_rooms)
        for y in xrange(self.grid.size_y):
            row = ''

            for x in xrange(self.grid.size_x):
                tile = self.grid[x, y]
                placed = False
                if tile.objects:
                    for obj in tile.objects:
                        if isinstance(obj, Door):
                            row += obj.is_open and '/' or '+'
                            placed = True
                            break
                    if placed:
                        continue
                if tile.type == TileType.WALL:
                    row += '#'
                elif tile.type == TileType.FLOOR:
                    row += '.'
                else:
                    row += ' '

            print row
