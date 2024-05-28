from battleship.game_simulator import *
from battleship.player import *

game = SingleOffenceGameSimulator(HuntAndTargetPlayer(), num_simulation=1000)
game.start()
