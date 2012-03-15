
import level_object
import components
import player
from actor import Actor, MoveAction, AttackAction, WaitAction
from position import Position
from render import Renderable
from temp import get_random_monster_params
from util import calc_distance


class InFOV(level_object.Component):

    COMPONENT_NAME = 'in_fov'

    def __init__(self):
        self.in_fov = False


def create_random_monster(x, y):
    name, tex = get_random_monster_params()

    monster = level_object.LevelObject(
        Actor(80, monster_act),
        Position(x, y, Position.ORDER_CREATURES),
        components.Movement(),
        Renderable(tex),
        components.Blocker(blocks_movement=True, bump_function=monster_bump),
        components.Fighter(2, 1, 0),
        InFOV(),
        level_object.Description(name),
    )
    return monster


def monster_act(actor):
    monster = actor.owner
    if monster.in_fov.in_fov:
        player = monster.level.game.player
        monster_pos = monster.position
        player_pos = player.position
        distance = calc_distance(monster_pos.x, monster_pos.y, player_pos.x, player_pos.y)
        if distance < 2:
            return AttackAction(player)
        else:
            dx = int(round((player_pos.x - monster_pos.x) / distance))
            dy = int(round((player_pos.y - monster_pos.y) / distance))
            return MoveAction(dx, dy)

    return WaitAction()


def monster_bump(blocker, who):
    monster = blocker.owner
    if who.has_component(player.Player) and who.has_component(components.Fighter) and monster.has_component(components.Fighter):
        who.fighter.do_attack(monster)
