import random

from util import randint_triangular


class TileGrid(object):

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self._contents = [LayoutGenerator.TILE_EMPTY for i in xrange(size_x * size_y)]

    def __getitem__(self, xy):
        x, y = xy
        return self._contents[y * self.size_x + x]

    def __setitem__(self, xy, tile):
        x, y = xy
        self._contents[y * self.size_x + x] = tile


class Room(object):

    def __init__(self, grid):
        self.grid = grid
        self.x = None
        self.y = None


class LayoutGenerator(object):

    TILE_EMPTY = ' '
    TILE_WALL = '#'
    TILE_FLOOR = '.'
    TILE_DOOR_CLOSED = '+'
    TILE_DOOR_OPEN = '/'

    def __init__(self, size_x, size_y, max_rooms=100, room_size_x=(7, 12), room_size_y=(7, 12), door_chance=0.75, open_door_chance=0.1):
        self.max_rooms = max_rooms
        self.room_size_x = room_size_x
        self.room_size_y = room_size_y
        self.door_chance = door_chance
        self.open_door_chance = open_door_chance
        self.grid = TileGrid(size_x, size_y)
        self.rooms = []

    def create_room(self):
        size_x = random.randint(*self.room_size_x)
        size_y = random.randint(*self.room_size_y)
        grid = TileGrid(size_x, size_y)

        for x in xrange(size_x):
            for y in xrange(size_y):
                if x == 0 or x == size_x - 1 or y == 0 or y == size_y - 1:
                    grid[x, y] = self.TILE_WALL
                else:
                    grid[x, y] = self.TILE_FLOOR

        return Room(grid)

    def place_room(self, room, x, y):
        room.x = x
        room.y = y
        self.rooms.append(room)

        for tile_x in xrange(room.grid.size_x):
            for tile_y in xrange(room.grid.size_y):
                tile = room.grid[tile_x, tile_y]
                if tile == self.TILE_EMPTY:
                    continue
                self.grid[x + tile_x, y + tile_y] = tile

    def choose_gate(self):
        room = random.choice(self.rooms)
        dir = random.choice('nsew')

        if dir == 'n':
            x = randint_triangular(room.x + 1, room.x + room.grid.size_x - 2)
            y = room.y + room.grid.size_y - 1
        elif dir == 's':
            x = randint_triangular(room.x + 1, room.x + room.grid.size_x - 2)
            y = room.y
        elif dir == 'e':
            x = room.x + room.grid.size_x - 1
            y = randint_triangular(room.y + 1, room.y + room.grid.size_y - 2)
        elif dir == 'w':
            x = room.x
            y = randint_triangular(room.y + 1, room.y + room.grid.size_y - 2)

        return x, y, dir

    def has_space_for_room(self, room, x, y):
        if x < 0 or x + room.grid.size_x >= self.grid.size_x or y < 0 or y + room.grid.size_y >= self.grid.size_y:
            return False

        for tile_x in xrange(room.grid.size_x):
            for tile_y in xrange(room.grid.size_y):
                if room.grid[tile_x, tile_y] != self.TILE_EMPTY and self.grid[x + tile_x, y + tile_y] != self.TILE_EMPTY:
                    return False

        return True

    def connect_rooms(self, x, y, dir):
        tiles = [self.TILE_FLOOR, self.TILE_FLOOR]

        if random.random() < self.door_chance:
            tile = random.random() < self.open_door_chance and self.TILE_DOOR_OPEN or self.TILE_DOOR_CLOSED
            tiles[random.randint(0, 1)] = tile

        off_x, off_y = {
            'n': (0, 1),
            's': (0, -1),
            'e': (1, 0),
            'w': (-1, 0)
        }[dir]

        self.grid[x, y] = tiles[0]
        self.grid[x + off_x, y + off_y] = tiles[1]

    def generate(self):
        room = self.create_room()
        x = (self.grid.size_x - room.grid.size_x) / 2
        y = (self.grid.size_y - room.grid.size_y) / 2
        self.place_room(room, x, y)

        for i in xrange(self.grid.size_x * self.grid.size_y * 2):
            if len(self.rooms) == self.max_rooms:
                break

            room = self.create_room()
            x, y, dir = self.choose_gate()

            if dir == 'n':
                room_x = x - randint_triangular(1, room.grid.size_x - 2)
                room_y = y + 1
            elif dir == 's':
                room_x = x - randint_triangular(1, room.grid.size_x - 2)
                room_y = y - room.grid.size_y
            elif dir == 'e':
                room_x = x + 1
                room_y = y - randint_triangular(1, room.grid.size_y - 1)
            elif dir == 'w':
                room_x = x - room.grid.size_x
                room_y = y - randint_triangular(1, room.grid.size_y - 1)

            if self.has_space_for_room(room, room_x, room_y):
                self.place_room(room, room_x, room_y)
                self.connect_rooms(x, y, dir)

    def in_bounds(self, x, y):
        return x >= 0 and x < self.grid.size_x and y >= 0 and y < self.grid.size_y

    def get_wall_transition(self, x, y):
        n = 1
        e = 2
        s = 4
        w = 8
        nw = 128
        ne = 16
        se = 32
        sw = 64

        def is_wall(x, y):
            if not self.in_bounds(x, y):
                return True
            return self.grid[x, y] in (self.TILE_WALL, self.TILE_EMPTY)

        v = 0
        if is_wall(x, y + 1):
            v |= n
        if is_wall(x + 1, y):
            v |= e
        if is_wall(x, y - 1):
            v |= s
        if is_wall(x - 1, y):
            v |= w
        if is_wall(x - 1, y + 1):
            v |= nw
        if is_wall(x + 1, y + 1):
            v |= ne
        if is_wall(x - 1, y - 1):
            v |= sw
        if is_wall(x + 1, y - 1):
            v |= se

        return v

    def print_grid(self):
        for y in xrange(self.grid.size_y):
            row = ''
            for x in xrange(self.grid.size_x):
                row += self.grid[x, y]
            print row


if __name__ == '__main__':
    g = LayoutGenerator(100, 100)
    g.generate()
    g.print_grid()
