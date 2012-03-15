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

    component_name = 'renderable'

    def __init__(self, tex, save_memento=False):
        self.sprite = pyglet.sprite.Sprite(tex)
        self.save_memento = save_memento

    def get_memento_sprite(self):
        return self.sprite


class LayoutRenderable(level_object.Component):

    component_name = 'layout_renderable'

    def __init__(self, tile):
        self.tile = tile