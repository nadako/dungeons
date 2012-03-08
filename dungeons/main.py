import pyglet

from dungeons.game import Game

game = Game()
game.start()

window = pyglet.window.Window(800, 600, 'Dungeon')
window.push_handlers(game)

pyglet.app.run()
