import pyglet

from game import Game

pyglet.options['debug_gl'] = False

window = pyglet.window.Window(1024, 768, 'Dungeon')

game = Game(window)
game.start()

pyglet.app.run()
