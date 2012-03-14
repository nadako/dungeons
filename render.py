import pyglet


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
