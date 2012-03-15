import random
import math

import pyglet

from level_object import Description


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


def get_name(entity):
    if not entity.has_component(Description):
        return 'Something'
    return entity.description.name
