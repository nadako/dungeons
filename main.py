import pyglet
pyglet.options['debug_gl'] = False

from game import Game

game = Game()
game.run()
