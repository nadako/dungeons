import pyglet


class LightOverlay(object):

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self._init_vlist()

    def _init_vlist(self):
        vertices = []
        colors = []

        for tile_y in xrange(self.size_y):
            for tile_x in xrange(self.size_x):
                x1 = tile_x * 8
                x2 = (tile_x + 1) * 8
                y1 = tile_y * 8
                y2 = (tile_y + 1) * 8
                c = (0, 0, 0, 255)
                vertices.extend((x1, y1, x2, y1, x2, y2, x1, y2))
                colors.extend((c * 4))

        self._vlist = pyglet.graphics.vertex_list(self.size_x * self.size_y * 4,
            ('v2i', vertices),
            ('c4B', colors)
        )

    def update_light(self, lightmap, memento):
        colors = []

        for tile_y in xrange(self.size_y):
            for tile_x in xrange(self.size_x):
                key = tile_x, tile_y
                intensity = lightmap.get(key)

                if intensity is None and key not in memento:
                    # if tile is not lit and not in memento, overlay it with opaque black
                    v = 255
                else:
                    # else calculate opacity based on light intensity
                    intensity = intensity or 0
                    v = int((1 - (0.3 + intensity * 0.7)) * 255)

                c = (0, 0, 0, v)
                colors.extend((c * 4))

        self._vlist.colors = colors

    def draw(self):
        self._vlist.draw(pyglet.gl.GL_QUADS)
