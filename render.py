import pyglet
import level_object


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


class Renderable(level_object.Component):

    COMPONENT_NAME = 'renderable'

    def __init__(self, tex, save_memento=False):
        self.sprite = pyglet.sprite.Sprite(tex)
        self.save_memento = save_memento

    def get_memento_sprite(self):
        return self.sprite


class LayoutRenderable(level_object.Component):

    COMPONENT_NAME = 'layout_renderable'

    def __init__(self, tile):
        self.tile = tile


class Camera(object):

    def __init__(self, window, zoom_factor, focus):
        self.window = window
        self.zoom_factor = zoom_factor
        self.focus = focus

    def __enter__(self):
        cam_x = self.window.width / 2 - self.focus.position.x * 8 * self.zoom_factor
        cam_y = self.window.height / 2 - self.focus.position.y * 8 * self.zoom_factor
        pyglet.gl.gl.glPushMatrix()
        pyglet.gl.gl.glTranslatef(cam_x, cam_y, 0)

    def __exit__(self, *exc):
        pyglet.gl.glPopMatrix()
