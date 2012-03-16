from actor import Action
from item import Item


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
        items = [e for e in entity.level.get_entities_at(pos.x, pos.y) if e is not entity and e.has(Item)]
        if items:
            item = items[-1]
            entity.level.remove_entity(item)
            entity.get(Inventory).pickup(item)
            if is_player(entity):
                entity.level.game.message('Picked up %d %s' % (item.get(Item).quantity, get_name(item)))
        elif is_player(entity):
            entity.level.game.message('Nothing to pickup here')


class DropAction(Action):

    def do(self, entity):
        inventory = entity.get(Inventory)
        if not inventory.items:
            if is_player(entity):
                entity.level.game.message('Nothing to drop')
        else:
            item = inventory.items[-1]
            inventory.items.remove(item)
            item_pos = item.get(Position)
            entity_pos = entity.get(Position)
            item_pos.x = entity_pos.x
            item_pos.y = entity_pos.y
            entity.level.add_entity(item)
            if is_player(entity):
                entity.level.game.message('Dropped up %s' % get_name(item))


from fight import Fighter
from inventory import Inventory
from player import is_player
from position import Position, Movement
from description import get_name
