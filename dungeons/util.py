import random

import pyglet


def randint_triangular(a, b):
    return int(round(random.triangular(a, b)))


def load_tilegrid(name):
    img = pyglet.resource.image(name)
    grid = pyglet.image.ImageGrid(img, img.height / 8, img.width / 8)
    return grid.get_texture_sequence()
