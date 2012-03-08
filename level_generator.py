import random

from util import randint_triangular


TILE_EMPTY = ' '
TILE_WALL = '#'
TILE_FLOOR = '.'
TILE_DOOR_CLOSED = '+'
TILE_DOOR_OPEN = '/'

DIR_N = (0, -1)
DIR_S = (0, 1)
DIR_W = (-1, 0)
DIR_E = (1, 0)


class LevelGenerator(object):

    def __init__(self, level):
        self.level = level

    def create_room(self):
        size_x = random.randint(7, 12)
        size_y = random.randint(7, 12)
        tiles = []
        for y in xrange(size_y):
            row = []
            for x in xrange(size_x):
                if x == 0 or x == size_x - 1 or y == 0 or y == size_y - 1:
                    row.append(TILE_WALL)
                else:
                    row.append(TILE_FLOOR)
            tiles.append(row)
        return Room(tiles)

    def place_room(self, room, x, y):
        room.x = x
        room.y = y
        self.level.rooms.append(room)

        for row in room.tiles:
            for tile in row:
                if tile == TILE_EMPTY:
                    continue
                self.level.set_tile(x, y, tile)
                x += 1
            y += 1
            x = room.x

    def choose_gate(self):
        room = random.choice(self.level.rooms)
        dir = random.choice((DIR_N, DIR_S, DIR_W, DIR_E))

        if dir is DIR_N:
            x = randint_triangular(room.x + 1, room.x + room.size_x - 2)
            y = room.y
        elif dir is DIR_S:
            x = randint_triangular(room.x + 1, room.x + room.size_x - 2)
            y = room.y + room.size_y - 1
        elif dir is DIR_W:
            x = room.x
            y = randint_triangular(room.y + 1, room.y + room.size_y - 2)
        elif dir is DIR_E:
            x = room.x + room.size_x - 1
            y = randint_triangular(room.y + 1, room.y + room.size_y - 2)

        return x, y, dir

    def has_space_for_room(self, room, x, y):
        if x < 0 or x + room.size_x > self.level.size_x or y < 0 or y + room.size_y > self.level.size_y:
            return False

        x1 = x
        for row in room.tiles:
            for tile in row:
                if (tile != TILE_EMPTY) and (self.level.get_tile(x, y) != TILE_EMPTY):
                    return False
                x +=1
            y += 1
            x = x1
        return True

    def connect_rooms(self, x, y, dir):
        tiles = [TILE_FLOOR, TILE_FLOOR]

        if random.random() < 0.75:
            tile = random.random() < 0.1 and TILE_DOOR_OPEN or TILE_DOOR_CLOSED
            tiles[random.randint(0, 1)] = tile

        self.level.set_tile(x, y, tiles[0])
        self.level.set_tile(x + dir[0], y + dir[1], tiles[1])

    def generate(self):
        room = self.create_room()
        x = (self.level.size_x - room.size_x) / 2
        y = (self.level.size_y - room.size_y) / 2
        self.place_room(room, x, y)

        for i in xrange(self.level.size_x * self.level.size_y * 2):
            room = self.create_room()
            x, y, dir = self.choose_gate()

            if dir is DIR_N:
                room_x = x - randint_triangular(1, room.size_x - 2)
                room_y = y - room.size_y
            elif dir is DIR_S:
                room_x = x - randint_triangular(1, room.size_x - 2)
                room_y = y + 1
            elif dir is DIR_W:
                room_x = x - room.size_x
                room_y = y - randint_triangular(1, room.size_y - 1)
            elif dir is DIR_E:
                room_x = x + 1
                room_y = y - randint_triangular(1, room.size_y - 1)

            if self.has_space_for_room(room, room_x, room_y):
                self.place_room(room, room_x, room_y)
                self.connect_rooms(x, y, dir)


class Room(object):

    def __init__(self, tiles):
        self.size_x = len(tiles[0])
        self.size_y = len(tiles)
        self.tiles = tiles
        self.x = None
        self.y = None
