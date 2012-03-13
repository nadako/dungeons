import level_object


class Inventory(level_object.Component):

    component_name = 'inventory'

    def __init__(self):
        self.items = []

    def pickup(self, item):
        assert (item.x, item.y) == (self.owner.x, self.owner.y)
        self.owner.level.remove_object(item)
        self.items.append(item)

    def drop(self, item):
        self.items.remove(item)
        self.owner.level.add_object(item, self.owner.x, self.owner.y)
