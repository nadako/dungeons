import pyglet
from pyglet.gl import *

zoom = 4
tile_size = 8
row = 4
margin = 4

img = pyglet.image.load('dungeon.png')
grid = pyglet.image.ImageGrid(img, img.height / tile_size, img.width / tile_size)

win = pyglet.window.Window(img.width * zoom + margin * grid.columns, tile_size * zoom * 2 + margin * 2, 'Tile numbers')
batch = pyglet.graphics.Batch()

drawables = []

x = margin
y = win.height - tile_size * zoom + margin

for col in xrange(grid.columns):
    label = pyglet.text.Label(str(col), 'sans-serif', 10, bold=True,
        x=x + tile_size * zoom / 2, y=y,
        anchor_y = 'bottom', anchor_x = 'center',
        batch=batch)
    drawables.append(label)

    sprite = pyglet.sprite.Sprite(grid[(grid.rows - 1 - row) * grid.columns + col], x, y - tile_size * zoom, batch=batch)
    sprite.scale = 4
    drawables.append(sprite)

    x += tile_size * zoom + margin

@win.event
def on_draw():
    win.clear()
    batch.draw()

pyglet.app.run()
