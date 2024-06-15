from battleship.game_simulator import *
from battleship.player import *

game = SingleOffenceGameSimulator(ProbabilityPlayer(), num_simulation=1, seed=777, tps=5)
game.start()

game = SingleOffenceGameSimulator(ProbabilityPlayer(), num_simulation=1000)
game.start()
