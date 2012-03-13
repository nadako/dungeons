import random

import level_object
import components
import player
from temp import monster_texes


def create_random_monster():
    monster = level_object.LevelObject(
        components.Actor(100, monster_act),
        components.Movement(),
        components.Renderable(random.choice(monster_texes)),
        components.Blocker(blocks_movement=True, bump_function=monster_bump),
        components.Fighter(2, 1, 0),
        level_object.Description('Goblin')
    )
    return monster


def monster_act(actor):
    dx = random.randint(-1, 1)
    dy = random.randint(-1, 1)
    actor.owner.movement.move(dx, dy)
    return 100


def monster_bump(blocker, who):
    monster = blocker.owner
    if who.has_component(player.Player) and who.has_component(components.Fighter) and monster.has_component(components.Fighter):
        who.fighter.do_attack(monster)
