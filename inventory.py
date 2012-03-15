import level_object


class Inventory(level_object.Component):

    COMPONENT_NAME = 'inventory'

    def __init__(self):
        self.items = []

    def pickup(self, item):
        assert (item.position.x, item.position.y) == (self.owner.position.x, self.owner.position.y)
        self.owner.level.remove_object(item)
        self.items.append(item)

    def drop(self, item):
        self.items.remove(item)
        item.position.x = self.owner.position.x
        item.position.y = self.owner.position.y
        self.owner.level.add_object(item)
