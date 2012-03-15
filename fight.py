import random

from entity import Component


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
        target_fighter.take_damage(dmg, self.owner)

    def take_damage(self, damage, source):
        self.health -= damage

        if is_player(source):
            source.level.game.message('You hit %s for %d hp' % (get_name(self.owner), damage))
        elif is_player(self.owner):
            self.owner.level.game.message('%s hits you for %d hp' % (get_name(source), damage))

        pos = self.owner.get(Position)
        self.owner.level.game.animate_damage(pos.x, pos.y, damage)

        if self.health <= 0:
            self.die()

    def die(self):
        if is_player(self.owner):
            self.owner.level.game.message('You die')
        else:
            self.owner.level.game.message('%s dies' % get_name(self.owner))

            pos = self.owner.get(Position)
            self.owner.level.add_entity(Entity(
                Renderable(random.choice(corpse_texes)),
                Description('%s\'s corpse' % get_name(self.owner)),
                Position(pos.x, pos.y, Position.ORDER_FLOOR + 1),
            ))
            self.owner.level.remove_entity(self.owner)


from description import Description, get_name
from entity import Entity
from player import is_player
from position import Position
from render import Renderable
from temp import corpse_texes
