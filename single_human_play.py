from battleship.game import *
from battleship.player import *

game = SingleOffenceGame(HumanPlayer(console_io=True))
game.start()
