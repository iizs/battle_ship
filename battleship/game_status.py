import logging
from .exception import *

logger = logging.getLogger(__name__)


class GameStatus:
    MARKER_EMPTY = '_'
    MARKER_MISS = '.'
    MARKER_HIT = 'X'
    MARKER_PATROL_BOAT = '1'
    MARKER_SUBMARINE = '2'
    MARKER_DESTROYER = '3'
    MARKER_BATTLESHIP = '4'
    MARKER_CARRIER = '5'
    SHIPS_AND_SIZES = {
        MARKER_PATROL_BOAT: 2,
        MARKER_SUBMARINE: 3,
        MARKER_DESTROYER: 3,
        MARKER_BATTLESHIP: 4,
        MARKER_CARRIER: 5,
    }

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.offence_turn = 1
        self.defence_board = [GameStatus.MARKER_EMPTY] * (self.size_x * self.size_y)
        self.offence_board = [GameStatus.MARKER_EMPTY] * (self.size_x * self.size_y)
        self.defence_shot_log = []
        self.offence_shot_log = []
        self.offence_enemy_sink_log = []
        self.defence_ships_hp = {
            GameStatus.MARKER_PATROL_BOAT: 2,
            GameStatus.MARKER_SUBMARINE: 3,
            GameStatus.MARKER_DESTROYER: 3,
            GameStatus.MARKER_BATTLESHIP: 4,
            GameStatus.MARKER_CARRIER: 5,
        }
        self.offence_ships_alive = 5
        self.defence_hp_sum = 17
        self.offence_hp_sum = 17
        self.game_over = False
        self.defence_win = False
        self.offence_win = False

    def print_offence_board(self):
        for x in range(10):
            print(' '.join(self.offence_board[x * self.size_x:(x + 1) * self.size_x]))

    def print_defence_board(self):
        for x in range(10):
            print(' '.join(self.defence_board[x * self.size_x:(x + 1) * self.size_x]))

    def print_all_board(self):
        pass

    def set_defence_board(self, board):
        if not self.__verify_board__(board):
            raise InvalidShipPlacementException()
        self.defence_board = board

    def add_offence_shot(self, shot, result, ship_sunk):
        shot_x, shot_y = self.__convert_shot_to_xy__(shot)
        shot_idx = self.__xy_to_idx__(shot_x, shot_y)

        # Something wrong
        assert self.offence_board[shot_idx] != GameStatus.MARKER_MISS \
               and self.offence_board[shot_idx] != GameStatus.MARKER_HIT

        self.offence_shot_log.append(shot)
        self.offence_board[shot_idx] = result

        if result == GameStatus.MARKER_HIT:
            self.offence_hp_sum -= 1
            if ship_sunk:
                self.offence_enemy_sink_log.append(self.offence_turn)
                self.offence_ships_alive -= 1
            if self.offence_hp_sum == 0:
                assert self.offence_ships_alive == 0  # Something wrong
                self.offence_win = True
                self.defence_win = False
                self.game_over = True

        self.offence_turn += 1

    def add_defence_shot(self, shot):
        shot_x, shot_y = self.__convert_shot_to_xy__(shot)
        shot_idx = self.__xy_to_idx__(shot_x, shot_y)

        if self.defence_board[shot_idx] == GameStatus.MARKER_MISS \
                or self.defence_board[shot_idx] == GameStatus.MARKER_HIT:
            raise InvalidShotException(f'Duplicated shot on {shot}')

        # Valid shot
        self.defence_shot_log.append(shot)

        if self.defence_board[shot_idx] == GameStatus.MARKER_EMPTY:
            # Missed
            self.defence_board[shot_idx] = GameStatus.MARKER_MISS
            return GameStatus.MARKER_MISS, False

        # Hit
        ship = self.defence_board[shot_idx]
        assert self.defence_ships_hp[ship] != 0  # Something wrong

        self.defence_board[shot_idx] = GameStatus.MARKER_HIT
        self.defence_ships_hp[ship] -= 1
        self.defence_hp_sum -= 1
        ship_sunk = (self.defence_ships_hp[ship] == 0)

        if self.defence_hp_sum == 0:
            self.defence_win = False
            self.offence_win = True
            self.game_over = True

        return GameStatus.MARKER_HIT, ship_sunk

    def __verify_board__(self, board):
        # TODO implement
        return True

    def __xy_to_idx__(self, x, y):
        return x * self.size_y + y

    def __convert_shot_to_xy__(self, shot: str):
        shot = shot.upper()
        if len(shot) < 2:
            raise InvalidShotException(f'Invalid coordinate, {shot}')
        x_part = shot[0]
        y_part = shot[1:]
        if x_part < 'A' or x_part > chr(ord('A') + self.size_x - 1):
            raise InvalidShotException(f'Invalid coordinate, {shot}')
        x = ord(shot[0]) - ord('A')
        try:
            y = int(y_part) - 1  # This can also raise ValueError()
            if y < 0 or y > (self.size_y - 1):
                raise ValueError()
        except ValueError:
            raise InvalidShotException(f'Invalid coordinate, {shot}')

        return x, y
