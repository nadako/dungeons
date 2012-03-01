from collections import deque

ACTION_COST = 100

class Actor(object):

    def __init__(self, speed, act=None):
        self.speed = speed
        self.energy = 0
        if act is not None:
            self.act = act

    def act(self):
        raise NotImplementedError()

class TimeSystem(object):

    def __init__(self, actors):
        self.actors = deque(actors)

    def tick(self):
        if self.actors:
            actor = self.actors[0]
            self.actors.rotate()
            actor.energy += actor.speed
            while actor.energy > 0:
                actor.energy -= actor.act()
