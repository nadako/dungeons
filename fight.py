import random

from entity import Component, Entity
from description import Description, get_name
from temp import corpse_texes
from render import Renderable
from position import Position


# This stuff is a mess
class Fighter(Component):

    COMPONENT_NAME = 'fighter'

    def __init__(self, max_health, attack, defense):
        self.health = self.max_health = max_health
        self.attack = attack
        self.defense = defense

    def do_attack(self, target):
        target_fighter = target.get(Fighter)
        dmg = max(0, self.attack - target_fighter.defense)
        self.owner.event('do_damage', dmg, target)
        target.event('take_damage', dmg, self.owner)

    def on_take_damage(self, amount, source):
        self.health -= amount

        pos = self.owner.get(Position)
        self.owner.level.game.animate_damage(pos.x, pos.y, amount)

        if self.health <= 0:
            self.die(source)

    def die(self, killer=None):
        self.owner.event('die')
        if killer:
            killer.event('kill', self.owner)

        if not is_player(self.owner):
            pos = self.owner.get(Position)
            self.owner.level.add_entity(Entity(
                Renderable(random.choice(corpse_texes)),
                Description('%s\'s corpse' % get_name(self.owner)),
                Position(pos.x, pos.y, Position.ORDER_FLOOR + 1),
            ))
            self.owner.level.remove_entity(self.owner)


from player import is_player
