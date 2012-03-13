import random

import level_object
import components
import player
from temp import monster_texes
from util import calc_distance


class InFOV(object):

    component_name = 'in_fov'

    def __init__(self):
        self.in_fov = False


def create_random_monster():
    monster = level_object.LevelObject(
        components.Actor(100, monster_act),
        components.Movement(),
        components.Renderable(random.choice(monster_texes)),
        components.Blocker(blocks_movement=True, bump_function=monster_bump),
        components.Fighter(2, 1, 0),
        InFOV(),
        level_object.Description('Goblin')
    )
    monster.order = level_object.LevelObject.ORDER_CREATURES
    return monster


def monster_act(actor):
    monster = actor.owner
    if monster.in_fov.in_fov:
        player = monster.level.game.player
        distance = calc_distance(monster.x, monster.y, player.x, player.y)
        if distance < 2:
            monster.fighter.do_attack(player)
        else:
            dx = int(round((player.x - monster.x) / distance))
            dy = int(round((player.y - monster.y) / distance))
            monster.movement.move(dx, dy)
    return 100


def monster_bump(blocker, who):
    monster = blocker.owner
    if who.has_component(player.Player) and who.has_component(components.Fighter) and monster.has_component(components.Fighter):
        who.fighter.do_attack(monster)
