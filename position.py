from level_object import Component


class Position(Component):

    component_name = 'position'

    ORDER_FLOOR = 0
    ORDER_WALLS = 10
    ORDER_FEATURES = 20
    ORDER_ITEMS = 30
    ORDER_CREATURES = 40
    ORDER_PLAYER = 50

    def __init__(self, x=0, y=0, order=ORDER_FLOOR):
        self.x = x
        self.y = y
        self.order = order
