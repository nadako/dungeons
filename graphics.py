import pyglet
from pyglet.gl import *

class TextureGroup(pyglet.graphics.TextureGroup):

    def set_state(self):
        super(TextureGroup, self).set_state()
        # remove smoothing when scaled in
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

class ShaderGroup(pyglet.graphics.Group):

    def __init__(self, shader, parent=None):
        super(ShaderGroup, self).__init__(parent)
        self.shader = shader

    def set_state(self):
        self.shader.bind()

    def unset_state(self):
        self.shader.unbind()
