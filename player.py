from entity import Component, Entity
from actor import Actor
from actions import MoveAction, PickupAction, WaitAction, DropAction
from blocker import Blocker
from fight import Fighter
from fov import FOV
from inventory import Inventory
from command import Command
from position import Position, Movement
from render import Renderable
from temp import player_tex


class Player(Component):

    COMPONENT_NAME = 'player'


def is_player(entity):
    return entity.has(Player)


def create_player(x, y):
    return Entity(
        Player(),
        Position(x, y, Position.ORDER_PLAYER),
        Actor(100, player_act),
        FOV(10),
        Movement(),
        Renderable(player_tex),
        Blocker(blocks_movement=True),
        Fighter(100, 1, 0),
        Inventory(),
    )


def player_act(player, level):
    command = level.game.get_command()
    level.game._message_log.mark_as_seen()

    if command.name == Command.MOVE:
        return MoveAction(*command.data)
    elif command.name == Command.PICKUP:
        return PickupAction()
    elif command.name == Command.DROP:
        return DropAction()

    return WaitAction()
