from actor import Action


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
        items = [o for o in entity.level.get_entities_at(pos.x, pos.y) if o is not entity]
        if items:
            item = items[-1]
            entity.get(Inventory).pickup(item)
            if is_player(entity):
                entity.level.game.message('Picked up %s' % get_name(item))
        elif is_player(entity):
            entity.level.game.message('Nothing to pickup here')


from fight import Fighter
from inventory import Inventory
from player import is_player
from position import Position, Movement
from description import get_name
