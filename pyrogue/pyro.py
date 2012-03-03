"""
Pyro: PYthon ROguelike by Eric D. Burgess, 2006
"""


# Pyro modules:
from util import *

import player
import dungeons
import io_curses as io


####################### CLASS DEFINITIONS #######################

class Pyro(object):
    "Main class in charge of running the game."
    def __init__(self):
        # Start a new game:
        self.game = Game()
    def Run(self):
        Global.IO.ClearScreen()
        try:
            while True:
                self.game.Update()
        except GameOver:
            Global.IO.DisplayText("Game over.  Character dump will go here when implemented.",
                                  c_yellow)
            log("Game ended normally.")
        
class Game(object):
    "Holds all game data; pickling this should be sufficient to save the game."
    def __init__(self):
        # Create the dungeon and the first level:
        self.dungeon = dungeons.Dungeon("Dingy Dungeon")
        self.current_level = self.dungeon.GetLevel(1)
        # Make the player character:
        self.pc = player.PlayerCharacter()
        # Put the PC on the up stairs:
        x, y = self.current_level.stairs_up
        self.current_level.AddCreature(self.pc, x, y)
    def Update(self):
        "Execute a single game turn."
        self.current_level.Update()
        
############################ MAIN ###############################

def StartGame():
    # Initialize the IO wrapper:
    Global.IO = io.IOWrapper()
    try:
        # Fire it up:
        Global.pyro = Pyro()
        Global.pyro.Run()
    finally:
        Global.IO.Shutdown()

if __name__ == "__main__":
    seed(3)
    PROFILE = False
    AUTO = False
    if AUTO or PROFILE:
        Global.KeyBuffer = "a\naaCbRqy "
        #Global.KeyBuffer = "a\naaRqy "
        seed(1)
    if PROFILE:
        import hotshot, hotshot.stats
        p = hotshot.Profile("pyro.prof")
        p.runcall(StartGame)
        p.close()
        stats = hotshot.stats.load("pyro.prof")
        stats.strip_dirs()
        stats.sort_stats("time", "calls")
        stats.print_stats(20)
    else:
        StartGame()
