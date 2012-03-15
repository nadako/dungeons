from entity import Component


class Position(Component):

    COMPONENT_NAME = 'position'

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


# TODO: this component is a mess, don't look there
class Movement(Component):

    COMPONENT_NAME = 'movement'

    def move(self, dx, dy):
        pos = self.owner.get(Position)
        new_x = pos.x + dx
        new_y = pos.y + dy

        blocker = self.owner.level.get_movement_blocker(new_x, new_y)
        if not blocker:
            self.owner.level.move_entity(self.owner, new_x, new_y)

            fov = self.owner.get(FOV)
            if fov:
                fov.update_light()
        elif isinstance(blocker, Blocker):
            blocker.bump(blocker, self.owner)


from entity import Entity
from blocker import Blocker
from fov import FOV
