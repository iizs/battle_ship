from battleship.game_simulator import *
from battleship.player import *

game = SingleOffenceGameSimulator(RandomPlayer())
game.start()
