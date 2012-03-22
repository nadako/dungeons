from entity import Component


class Health(Component):

    COMPONENT_NAME = 'health'

    def __init__(self, max_health):
        self.health = self.max_health = max_health

    def on_take_damage(self, amount, source):
        self.health -= amount
        if self.health <= 0:
            self.die(source)

    def die(self, killer=None):
        self.owner.event('die')
        if killer:
            killer.event('kill', self.owner)
