from entity import Component
from description import get_name
from player import is_player


class Blocker(Component):

    COMPONENT_NAME = 'blocker'

    def __init__(self, blocks_sight=False, blocks_movement=False, bump_function=None):
        self.blocks_sight = blocks_sight
        self.blocks_movement = blocks_movement
        self.bump_function = bump_function or self.default_bump

    @staticmethod
    def default_bump(blocker, who):
        if is_player(who):
            who.level.game.message('You bump into %s' % get_name(blocker.owner))
