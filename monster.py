from blocker import Blocker
from description import Description
from entity import Entity
from fight import Fighter
from actor import Actor
from actions import MoveAction, AttackAction, WaitAction
from fov import InFOV
from player import is_player
from position import Position, Movement
from render import Renderable
from temp import get_random_monster_params
from util import calc_distance


def create_random_monster(x, y):
    name, tex = get_random_monster_params()
    monster = Entity(
        Actor(80, monster_act),
        Position(x, y, Position.ORDER_CREATURES),
        Movement(),
        Renderable(tex),
        Blocker(blocks_movement=True, bump_function=monster_bump),
        Fighter(2, 1, 0),
        InFOV(),
        Description(name),
    )
    return monster


def monster_act(monster, level):
    if monster.get(InFOV).in_fov:
        player = level.game.player
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
