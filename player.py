from inventory import Inventory
import level_object
import components

from command import Command
from temp import player_tex


class Player(level_object.Component):

    component_name = 'player'


def is_player(obj):
    return obj.has_component(Player)


def create_player():
    player = level_object.LevelObject(
        Player(),
        Actor(100, player_act),
        components.FOV(10),
        components.Movement(),
        components.Renderable(player_tex),
        components.Blocker(blocks_movement=True),
        components.Fighter(100, 1, 0),
        Inventory(),
    )
    player.order = level_object.LevelObject.ORDER_PLAYER
    return player


def player_act(actor):
    player = actor.owner
    command = player.level.game.get_command()

    player.level.game._message_log.mark_as_seen()

    if command.name == Command.MOVE:
        return MoveAction(*command.data)
    elif command.name == Command.PICKUP:
        return PickupAction()

    return WaitAction()


from actor import Actor, MoveAction, PickupAction, WaitAction
