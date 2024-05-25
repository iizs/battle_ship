import logging
from .exception import *
from .game_status import GameStatus
from .player import RandomPlayer

logger = logging.getLogger(__name__)


class SingleOffenceGame:
    SIZE_X = 10
    SIZE_Y = 10

    def __init__(self, player):
        self.player = player
        self.npc_player = RandomPlayer()
        self.player_game_status = None
        self.npc_game_status = None

    def start(self):
        self.player_game_status = GameStatus(SingleOffenceGame.SIZE_X, SingleOffenceGame.SIZE_Y)
        self.npc_game_status = GameStatus(SingleOffenceGame.SIZE_X, SingleOffenceGame.SIZE_Y)
        self.npc_player.update_game_status(self.npc_game_status)
        self.npc_game_status.set_defence_board(self.npc_player.place_ships())
        self.player.update_game_status(self.player_game_status)
        while not self.player_game_status.game_over:
            self.player_game_status.print_offence_board()
            shot = self.player.shoot()
            try:
                shot_result, ship_sunk = self.npc_game_status.add_defence_shot(shot)
                self.player_game_status.add_offence_shot(shot, shot_result, ship_sunk)
            except InvalidShotException as e:
                logger.warning(e)

        self.player.update_game_status(self.player_game_status)
        self.player_game_status.print_offence_board()
