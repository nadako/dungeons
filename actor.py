from collections import deque

from entity import Component


class Actor(Component):

    COMPONENT_NAME = 'actor'

    def __init__(self, speed, act_function):
        self.energy = 0
        self.speed = speed
        self.act_function = act_function


class Action(object):

    cost = 100


class ActorSystem(object):

    def __init__(self, level):
        self._entities = deque()
        self._level = level

    def add_entity(self, entity):
        self._entities.append(entity)

    def remove_entity(self, entity):
        self._entities.remove(entity)

    def update(self):
        if self._entities:
            entity = self._entities[0]
            self._entities.rotate()
            actor = entity.get(Actor)
            actor.energy += actor.speed
            while actor.energy > 0:
                action = actor.act_function(entity, self._level, self._level.game)
                actor.energy -= action.cost
                action.do(entity)
