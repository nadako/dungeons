from entity import Component
from position import Position


class Inventory(Component):

    COMPONENT_NAME = 'inventory'

    def __init__(self):
        self.items = []

    def pickup(self, item):
        self.owner.level.remove_entity(item)
        self.items.append(item)

    def drop(self, item):
        self.items.remove(item)
        item_pos = item.get(Position)
        owner_pos = self.owner.get(Position)
        item_pos.x = owner_pos.x
        item_pos.y = owner_pos.y
        self.owner.level.add_entity(item)
