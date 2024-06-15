from battleship.game_simulator import *
from battleship.player import *

game = SingleOffenceGameSimulator(RandomPlayer(), num_simulation=1, seed=777, tps=10)
game.start()

game = SingleOffenceGameSimulator(RandomPlayer(), num_simulation=1000)
game.start()
