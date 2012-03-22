from actor import Action
from item import Item
from fight import Fighter
from inventory import Inventory
from position import Position, Movement


class WaitAction(Action):

    def do(self, entity):
        pass


class MoveAction(Action):

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def do(self, entity):
        entity.get(Movement).move(self.dx, self.dy)


class AttackAction(Action):

    def __init__(self, target):
        self.target = target

    def do(self, entity):
        entity.get(Fighter).do_attack(self.target)


class PickupAction(Action):

    def do(self, entity):
        pos = entity.get(Position)
        items = [e for e in entity.level.position_system.get_entities_at(pos.x, pos.y) if e is not entity and e.has(Item)]
        if items:
            item = items[-1]
            entity.level.remove_entity(item)
            entity.get(Inventory).pickup(item)
        else:
            item = None

        entity.event('pickup', item)


class DropAction(Action):

    def do(self, entity):
        inventory = entity.get(Inventory)
        if inventory.items:
            item = inventory.items[-1]
            inventory.items.remove(item)
            item_pos = item.get(Position)
            entity_pos = entity.get(Position)
            item_pos.x = entity_pos.x
            item_pos.y = entity_pos.y
            entity.level.add_entity(item)
        else:
            item = None

        entity.event('drop', item)
