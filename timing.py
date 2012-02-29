from collections import deque

class Actor(object):

    def __init__(self, speed):
        self.speed = speed
        self.energy = 0

    def act(self):
        raise NotImplementedError()

class Game(object):

    def __init__(self, actors):
        self.actors = deque(actors)

    def tick(self):
        if self.actors:
            actor = self.actors[0]
            self.actors.rotate()
            actor.energy += actor.speed
            while actor.energy > 0:
                actor.energy -= actor.act()


ACTION_COST = 100

class Monster(Actor):

    def __init__(self, name, speed):
        self.name = name
        super(Monster, self).__init__(speed)

    def act(self):
        print 'Monster %s acts!' % self.name
        return ACTION_COST

class Player(Actor):

    def act(self):
        print 'Player acts! (press enter)'
        raw_input()
        return ACTION_COST

game = Game([
    Player(100),
    Monster('The Swift One', 200),
    Monster('Slowpoke', 50),
])

while True:
    game.tick()
