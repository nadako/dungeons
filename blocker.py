from entity import Component
from util import event_property


class Blocker(Component):

    COMPONENT_NAME = 'blocker'

    def __init__(self, blocks_sight=False, blocks_movement=False, bump_function=None):
        self._blocks_sight = blocks_sight
        self.blocks_movement = blocks_movement
        self.bump_function = bump_function or self.default_bump

    blocks_sight = event_property('_blocks_sight', 'blocks_sight_change')

    @staticmethod
    def default_bump(blocker, who):
        who.event('bump', blocker.owner)
