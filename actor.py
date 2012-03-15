from entity import Component


class Actor(Component):

    COMPONENT_NAME = 'actor'

    def __init__(self, speed, act_function):
        self.energy = 0
        self.speed = speed
        self.act_function = act_function


class Action(object):

    cost = 100
