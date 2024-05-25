from battleship.game import *
from battleship.player import *

game = SingleOffenceGame(RandomPlayer(console_io=True))
game.start()
