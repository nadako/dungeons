import random
import pyglet

import level_object
import player
import shadowcaster
from temp import corpse_texes


class Blocker(level_object.Component):

    component_name = 'blocker'

    def __init__(self, blocks_sight=False, blocks_movement=False, bump_function=None):
        self.blocks_sight = blocks_sight
        self.blocks_movement = blocks_movement
        if bump_function:
            self.bump = bump_function

    @staticmethod
    def bump(blocker, who):
        if who.has_component(player.Player):
            who.level.game.message('You bump into %s' % blocker.owner.name)


class Actor(level_object.Component):

    component_name = 'actor'

    def __init__(self, speed, act=None):
        self.energy = 0
        self.speed = speed
        self._act = act

    def act(self):
        if self._act is None:
            raise NotImplementedError()
        return self._act(self)


class FOV(level_object.Component):

    component_name = 'fov'

    def __init__(self, radius):
        self.radius = radius
        self.lightmap = {}

    def update_light(self):
        self.lightmap.clear()
        self.lightmap[self.owner.x, self.owner.y] = 1
        caster = shadowcaster.ShadowCaster(self.owner.level.blocks_sight, self.set_light)
        caster.calculate_light(self.owner.x, self.owner.y, self.radius)
        self.on_fov_updated()

    def set_light(self, x, y, intensity):
        self.lightmap[x, y] = intensity

    def is_in_fov(self, x, y):
        return self.lightmap.get((x, y), 0) > 0

    def on_fov_updated(self):
        pass


class Movement(level_object.Component):

    component_name = 'movement'

    def move(self, dx, dy):
        new_x = self.owner.x + dx
        new_y = self.owner.y + dy

        blocker = self.owner.level.blocks_movement(new_x, new_y)
        if not blocker:
            self.owner.level.move_object(self.owner, new_x, new_y)
        elif isinstance(blocker, level_object.LevelObject):
            blocker.blocker.bump(blocker.blocker, self.owner)

        # TODO: use some kind of events/signals
        if self.owner.has_component(FOV):
            self.owner.fov.update_light()


class Renderable(level_object.Component):

    component_name = 'renderable'

    def __init__(self, tex, save_memento=False):
        self.sprite = pyglet.sprite.Sprite(tex)
        self.save_memento = save_memento

    def get_memento_sprite(self):
        return self.sprite


class Fighter(level_object.Component):

    component_name = 'fighter'

    def __init__(self, max_health, attack, defense):
        self.health = self.max_health = max_health
        self.attack = attack
        self.defense = defense

    def do_attack(self, target):
        dmg = max(0, self.attack - target.fighter.defense)
        target.fighter.take_damage(dmg, self.owner)

    def take_damage(self, damage, source):
        self.health -= damage

        if source.has_component(player.Player):
            source.level.game.message('You hit %s for %d hp' % (self.owner.name, damage))
        if self.health <= 0:
            self.die()

    def die(self):
        self.owner.level.game.message('%s dies' % self.owner.name)
        corpse = level_object.LevelObject(Renderable(random.choice(corpse_texes)))
        self.owner.level.add_object(corpse, self.owner.x, self.owner.y)
        self.owner.level.remove_object(self.owner)
