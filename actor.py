import level_object


class Actor(level_object.Component):

    component_name = 'actor'

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
        items = obj.level.get_objects_at(obj.x, obj.y)
        if items:
            obj.inventory.pickup(items[0])
