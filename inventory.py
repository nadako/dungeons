from entity import Component


class Inventory(Component):

    COMPONENT_NAME = 'inventory'

    def __init__(self):
        self.items = []
