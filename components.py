class Position(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Renderable(object):

    def __init__(self, sprite):
        self.sprite = sprite
