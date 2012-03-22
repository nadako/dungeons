from entity import Component


class Blocker(Component):

    COMPONENT_NAME = 'blocker'

    def __init__(self, blocks_sight=False, blocks_movement=False, bump_function=None):
        self._blocks_sight = blocks_sight
        self.blocks_movement = blocks_movement
        self.bump_function = bump_function or self.default_bump

    @property
    def blocks_sight(self):
        return self._blocks_sight

    @blocks_sight.setter
    def blocks_sight(self, value):
        if value != self._blocks_sight:
            self._blocks_sight = value
            self.owner.event('blocks_sight_change')

    @staticmethod
    def default_bump(blocker, who):
        who.event('bump', blocker.owner)
