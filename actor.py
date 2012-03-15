import level_object
from player import is_player
from util import get_name


class Actor(level_object.Component):

    COMPONENT_NAME = 'actor'

    def __init__(self, speed, act=None):
        self.energy = 0
        self.speed = speed
        self._act = act

    def act(self):
        if self._act is None:
            raise NotImplementedError()
        return self._act(self)


class Action(object):

    cost = 100


class WaitAction(Action):

    def do(self, obj):
        pass


class MoveAction(Action):

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def do(self, obj):
        obj.movement.move(self.dx, self.dy)


class AttackAction(Action):

    def __init__(self, target):
        self.target = target

    def do(self, obj):
        obj.fighter.do_attack(self.target)


class PickupAction(Action):

    def do(self, obj):
        pos = obj.position
        items = [o for o in obj.level.get_objects_at(pos.x, pos.y) if o is not obj]
        if items:
            item = items[-1]
            obj.inventory.pickup(item)
            if is_player(obj):
                obj.level.game.message('Picked up %s' % get_name(item))
        elif is_player(obj):
            obj.level.game.message('Nothing to pickup here')
