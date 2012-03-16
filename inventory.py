from entity import Component
from item import Item


class Inventory(Component):

    COMPONENT_NAME = 'inventory'

    def __init__(self):
        self.items = []

    def pickup(self, item):
        item_component = item.get(Item)

        if item_component.stackable:
            for other in self.items:
                other_item_component = other.get(Item)
                if other_item_component.stacks_with(item_component):
                    other_item_component.quantity += item_component.quantity
                    return

        self.items.append(item)
