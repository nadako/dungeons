import heapq


class Tile(object):

    def __init__(self, type):
        self.type = type
        self._objects = []

    def add_object(self, object):
        if object not in self._objects:
            heapq.heappush(self._objects, object)

    def remove_object(self, object):
        self._objects.remove(object)

    @property
    def objects(self):
        return tuple(self._objects)

    @property
    def is_transparent(self):
        if not self.type.is_transparent:
            return False

        for obj in self._objects:
            if not obj.is_transparent:
                return False

        return True

    @property
    def is_passable(self):
        if not self.type.is_passable:
            return False

        for obj in self._objects:
            if not obj.is_passable:
                return False

        return True

    def bump(self, creature):
        for object in self.objects:
            object.bump(creature)

class TileType(object):

    def __init__(self, name, is_transparent, is_passable):
        self.name = name
        self.is_transparent = is_transparent
        self.is_passable = is_passable


TileType.EMPTY = TileType(u'Void', True, True)
TileType.FLOOR = TileType(u'Floor', True, True)
TileType.WALL = TileType(u'Wall', False, False)

class TileObject(object):

    def __init__(self, order=0):
        self._order = order

    @property
    def is_transparent(self):
        return True

    @property
    def is_passable(self):
        return True

    def bump(self, creature):
        pass

    def __lt__(self, other):
        if not isinstance(other, TileObject):
            raise RuntimeError('Comparing TileObject with object of another type: %r, %r' % (other, other.__class__), other)
        return self._order > other._order


class Door(TileObject):

    def __init__(self, is_open=False):
        super(Door, self).__init__(order=0)
        self.is_open = is_open

    @property
    def is_transparent(self):
        return self.is_open

    @property
    def is_passable(self):
        return self.is_open

    def bump(self, creature):
        self.is_open = not self.is_open


class TileGrid(object):

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.clear()

    def clear(self):
        self._tiles = [Tile(TileType.EMPTY) for _ in xrange(self.size_x * self.size_y)]

    def __getitem__(self, position):
        x, y = position
        return self._tiles[y * self.size_x + x]
