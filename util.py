import random
import math

import pyglet


def randint_triangular(a, b):
    return int(round(random.triangular(a, b)))


def load_tilegrid(name):
    img = pyglet.resource.image(name)
    grid = pyglet.image.ImageGrid(img, img.height / 8, img.width / 8)
    return grid.get_texture_sequence()


def calc_distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx ** 2 + dy ** 2)


def event_property(attr, event):
    def fget(self, attr=attr):
        return getattr(self, attr)
    def fset(self, value, attr=attr, event=event):
        if value != getattr(self, attr):
            setattr(self, attr, value)
            self.owner.event(event)
    return property(fget, fset)
