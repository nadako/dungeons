import random
import pyglet

from entity import Component
from generator import LayoutGenerator
from light import LightOverlay
from position import Position
from temp import floor_tex, get_wall_tex, dungeon_tex
from util import event_property


class TextureGroup(pyglet.graphics.TextureGroup):
    """A batch group that binds texture and sets mag filter to NEAREST not to screw our pretty pixel art"""

    def set_state(self):
        super(TextureGroup, self).set_state()
        pyglet.gl.glTexParameteri(self.texture.target, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)


class ZoomGroup(pyglet.graphics.Group):

    def __init__(self, zoom, parent=None):
        super(ZoomGroup, self).__init__(parent)
        self.zoom = zoom

    def set_state(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glScalef(self.zoom, self.zoom, 1)

    def unset_state(self):
        pyglet.gl.glPopMatrix()

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self.zoom == other.zoom and
            self.parent == other.parent
        )

    def __hash__(self):
        return hash((self.zoom, self.parent))

    def __repr__(self):
        return '%s(zoom=%d)' % (self.__class__.__name__, self.zoom)


class CameraGroup(pyglet.graphics.Group):

    def __init__(self, window, zoom_factor, focus=None, parent=None):
        super(CameraGroup, self).__init__(parent)
        self.window = window
        self.zoom_factor = zoom_factor
        self.focus = focus

    def set_state(self):
        if self.focus is not None:
            pos = self.focus.get(Position)
            cam_x = self.window.width / 2 - pos.x * 8 * self.zoom_factor
            cam_y = self.window.height / 2 - pos.y * 8 * self.zoom_factor
            pyglet.gl.gl.glPushMatrix()
            pyglet.gl.gl.glTranslatef(cam_x, cam_y, 0)

    def unset_state(self):
        if self.focus is not None:
            pyglet.gl.glPopMatrix()

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self.window is other.window and
            self.zoom_factor == other.zoom_factor and
            self.parent == other.parent
            )

    def __hash__(self):
        return hash((self.window, self.zoom_factor, self.parent))


class Animation(object):

    def __init__(self, duration):
        self.anim_time = 0.0
        self.duration = duration
        pyglet.clock.schedule(self.animate)

    def cancel(self):
        pyglet.clock.unschedule(self.animate)
        self.finish()

    def animate(self, dt):
        self.anim_time += dt
        if self.anim_time > self.duration:
            self.cancel()
            return
        self.update()

    def finish(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()


class Renderable(Component):

    COMPONENT_NAME = 'renderable'

    def __init__(self, image):
        self._image = image

    image = event_property('_image', 'image_change')


class LayoutRenderable(Component):

    COMPONENT_NAME = 'layout_renderable'

    def __init__(self, tile):
        self.tile = tile


class RenderSystem(object):

    zoom = 3

    def __init__(self, window):
        self._window = window
        self._batch = pyglet.graphics.Batch()
        self._text_overlay_batch = pyglet.graphics.Batch() # TODO: why doesnt it work in the main batch?
        self._animations = set()
        self._sprites = {}
        self._level_vlist = None
        self._light_overlay = None
        self.camera = CameraGroup(self._window, self.zoom)
        self._zoom_group = ZoomGroup(self.zoom, self.camera)

    def render_level(self, level):
        vertices = []
        tex_coords = []

        for x in xrange(level.size_x):
            for y in xrange(level.size_y):
                x1 = x * 8
                x2 = x1 + 8
                y1 = y * 8
                y2 = y1 + 8

                for entity in level.position_system.get_entities_at(x, y):
                    renderable = entity.get(LayoutRenderable)
                    if renderable:
                        tile = renderable.tile
                        break
                else:
                    continue

                # always add floor, because we wanna draw walls above floor
                vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
                tex_coords.extend(floor_tex.tex_coords)

                if tile == LayoutGenerator.TILE_WALL:
                    # if we got wall, draw it above floor
                    tex = get_wall_tex(level.get_wall_transition(x, y))
                    vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
                    tex_coords.extend(tex.tex_coords)

        group = TextureGroup(dungeon_tex, pyglet.graphics.OrderedGroup(Position.ORDER_FLOOR, self._zoom_group))
        self._level_vlist = self._batch.add(len(vertices) / 2, pyglet.gl.GL_QUADS, group,
            ('v2i/static', vertices),
            ('t3f/statc', tex_coords),
        )

        group = pyglet.graphics.OrderedGroup(Position.ORDER_PLAYER + 1, self._zoom_group)
        self._light_overlay = LightOverlay(level.size_x, level.size_y, self._batch, group)

    def update_light(self, lightmap, memory):
        self._light_overlay.update_light(lightmap, memory)

    def add_entity(self, entity):
        image = entity.get(Renderable).image
        pos = entity.get(Position)
        group = pyglet.graphics.OrderedGroup(pos.order, self._zoom_group)
        sprite = pyglet.sprite.Sprite(image, pos.x * 8, pos.y * 8, batch=self._batch, group=group)
        self._sprites[entity] = sprite
        entity.listen('image_change', self._on_image_change)
        entity.listen('move', self._on_move)

    def remove_entity(self, entity):
        sprite = self._sprites.pop(entity)
        sprite.delete()
        entity.unlisten('image_change', self._on_image_change)
        entity.unlisten('move', self._on_move)

    def _on_image_change(self, entity):
        self._sprites[entity].image = entity.get(Renderable).image

    def _on_move(self, entity, old_x, old_y, new_x, new_y):
        self._sprites[entity].set_position(new_x * 8, new_y * 8)

    def draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self._batch.draw()
        self._text_overlay_batch.draw()

    def dispose(self):
        for sprite in self._sprites.values():
            sprite.delete()
        self._sprites.clear()

        if self._level_vlist:
            self._level_vlist.delete()
            self._level_vlist = None

        if self._light_overlay:
            self._light_overlay.delete()
            self._light_overlay = None

        for anim in self._animations:
            anim.cancel()
        self._animations.clear()

    def animate_damage(self, x, y, dmg):
        # hacky hack
        x = (x * 8 + random.randint(2, 6)) * self.zoom
        start_y = (y * 8 + random.randint(0, 4)) * self.zoom

        label = pyglet.text.Label('-' + str(dmg), font_name='eight2empire', color=(255, 0, 0, 255),
            x=x, y=start_y, anchor_x='center', anchor_y='bottom',
            batch=self._text_overlay_batch, group=self.camera)

        anim = Animation(1)

        def update_label(animation=anim):
            label.y = start_y + 12 * self.zoom * animation.anim_time
            alpha = int((1.0 - animation.anim_time / animation.duration) * 255)
            label.color = (255, 0, 0, alpha)

        anim.update = update_label
        anim.finish = label.delete
        self._animations.add(anim)
