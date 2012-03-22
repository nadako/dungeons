import pyglet

from entity import Component
from position import Position
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
        self._batch.draw()
