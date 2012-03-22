import random

from blocker import Blocker
from description import Description, get_name
from entity import Entity, Component
from fight import Fighter
from actor import Actor
from actions import MoveAction, AttackAction, WaitAction
from fov import InFOV
from health import Health
from player import is_player
from position import Position, Movement
from render import Renderable
from temp import get_random_monster_params, corpse_texes
from util import calc_distance


def create_random_monster(x, y):
    name, tex = get_random_monster_params()
    monster = Entity(
        Actor(80, monster_act),
        Position(x, y, Position.ORDER_CREATURES),
        Movement(),
        Renderable(tex),
        Blocker(blocks_movement=True, bump_function=monster_bump),
        Health(2),
        Fighter(1, 0),
        CorpseGenerator(),
        InFOV(),
        Description(name),
    )
    return monster


def monster_act(monster, level, game):
    if monster.get(InFOV).in_fov:
        player = game.player
        monster_pos = monster.get(Position)
        player_pos = player.get(Position)
        distance = calc_distance(monster_pos.x, monster_pos.y, player_pos.x, player_pos.y)
        if distance < 2:
            return AttackAction(player)
        else:
            dx = int(round((player_pos.x - monster_pos.x) / distance))
            dy = int(round((player_pos.y - monster_pos.y) / distance))
            return MoveAction(dx, dy)

    return WaitAction()


def monster_bump(blocker, who):
    if is_player(who):
        who.get(Fighter).do_attack(blocker.owner)


class CorpseGenerator(Component):

    def on_die(self):
        pos = self.owner.get(Position)
        corpse = Entity(
            Renderable(random.choice(corpse_texes)),
            Description('%s\'s corpse' % get_name(self.owner)),
            Position(pos.x, pos.y, Position.ORDER_FLOOR + 1),
        )
        self.owner.level.add_entity(corpse)
        self.owner.level.remove_entity(self.owner)
