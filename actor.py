from entity import Component


class Actor(Component):

    COMPONENT_NAME = 'actor'

    def __init__(self, speed, act_function=None):
        self.energy = 0
        self.speed = speed
        self._act_function = act_function

    def act(self):
        if self._act_function is None:
            raise NotImplementedError()
        return self._act_function(self)


class Action(object):

    cost = 100
