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


class Camera(object):

    def __init__(self, window, zoom_factor, focus):
        self.window = window
        self.zoom_factor = zoom_factor
        self.focus = focus

    def __enter__(self):
        pos = self.focus.get(Position)
        cam_x = self.window.width / 2 - pos.x * 8 * self.zoom_factor
        cam_y = self.window.height / 2 - pos.y * 8 * self.zoom_factor
        pyglet.gl.gl.glPushMatrix()
        pyglet.gl.gl.glTranslatef(cam_x, cam_y, 0)

    def __exit__(self, *exc):
        pyglet.gl.glPopMatrix()


class RenderSystem(object):

    def __init__(self):
        self._batch = pyglet.graphics.Batch()
        self._sprites = {}
        self._level_vlist = None
        self._light_overlay = None

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

        group = TextureGroup(dungeon_tex, pyglet.graphics.OrderedGroup(Position.ORDER_FLOOR))
        self._level_vlist = self._batch.add(len(vertices) / 2, pyglet.gl.GL_QUADS, group,
            ('v2i/static', vertices),
            ('t3f/statc', tex_coords),
        )

        self._light_overlay = LightOverlay(level.size_x, level.size_y, self._batch)

    def update_light(self, lightmap, memory):
        self._light_overlay.update_light(lightmap, memory)

    def add_entity(self, entity):
        image = entity.get(Renderable).image
        pos = entity.get(Position)
        group = pyglet.graphics.OrderedGroup(pos.order)
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
