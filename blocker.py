from entity import Component


class Blocker(Component):

    COMPONENT_NAME = 'blocker'

    def __init__(self, blocks_sight=False, blocks_movement=False, bump_function=None):
        self.blocks_sight = blocks_sight
        self.blocks_movement = blocks_movement
        if bump_function:
            self.bump = bump_function

    @staticmethod
    def bump(blocker, who):
        if is_player(who):
            who.level.game.message('You bump into %s' % get_name(blocker.owner))


from player import is_player
from description import get_name
