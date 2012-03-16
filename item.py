from entity import Component


class Item(Component):

    def __init__(self, type_name, stackable=True, quantity=1):
        self.type_name = type_name
        self.stackable = stackable
        self.quantity = quantity

    def stacks_with(self, other_item):
        if self.stackable and other_item.type_name == self.type_name:
            return True
        else:
            return False
