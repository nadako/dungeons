from entity import Component
from position import Position
from shadowcaster import ShadowCaster


class FOV(Component):

    COMPONENT_NAME = 'fov'

    def __init__(self, radius):
        self.radius = radius
        self.lightmap = {}

    def update_light(self):
        old_lightmap = self.lightmap.copy()
        pos = self.owner.get(Position)
        self.lightmap.clear()
        self.lightmap[pos.x, pos.y] = 1
        caster = ShadowCaster(self.owner.level.get_sight_blocker, self._set_light)
        caster.calculate_light(pos.x, pos.y, self.radius)
        self.on_update(old_lightmap, self.lightmap)

    def _set_light(self, x, y, intensity):
        self.lightmap[x, y] = intensity

    def on_update(self, old_lightmap, new_lightmap):
        pass

    def is_in_fov(self, x, y):
        return self.lightmap.get((x, y), 0) > 0


class InFOV(Component):

    COMPONENT_NAME = 'in_fov'

    def __init__(self):
        self.in_fov = False
