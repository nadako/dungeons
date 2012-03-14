import pyglet


class Camera(object):

    def __init__(self, window, zoom_factor, focus):
        self.window = window
        self.zoom_factor = zoom_factor
        self.focus = focus

    def __enter__(self):
        cam_x = self.window.width / 2 - self.focus.x * 8 * self.zoom_factor
        cam_y = self.window.height / 2 - self.focus.y * 8 * self.zoom_factor
        pyglet.gl.gl.glPushMatrix()
        pyglet.gl.gl.glTranslatef(cam_x, cam_y, 0)

    def __exit__(self, *exc):
        pyglet.gl.glPopMatrix()
