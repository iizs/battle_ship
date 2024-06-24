import logging
from .exception import *

logger = logging.getLogger(__name__)


class GameStatus:
    MARKER_EMPTY = '.'
    MARKER_MISS = 'o'
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
        self.offence_ships_alive = [
            GameStatus.MARKER_PATROL_BOAT,
            GameStatus.MARKER_SUBMARINE,
            GameStatus.MARKER_DESTROYER,
            GameStatus.MARKER_BATTLESHIP,
            GameStatus.MARKER_CARRIER,
        ]
        self.defence_hp_sum = 17
        self.offence_hp_sum = 17
        self.game_over = False
        self.defence_win = False
        self.offence_win = False

    def print_offence_board(self):
        print('  1 2 3 4 5 6 7 8 9 10')
        for x in range(10):
            print(chr(x + ord('A')) + ' ' + ' '.join(self.offence_board[x * self.size_x:(x + 1) * self.size_x]))

    def print_defence_board(self):
        print('  1 2 3 4 5 6 7 8 9 10')
        for x in range(10):
            print(chr(x + ord('A')) + ' ' + ' '.join(self.defence_board[x * self.size_x:(x + 1) * self.size_x]))

    def print_all_board(self):
        pass

    def set_defence_board(self, board):
        if not self.__verify_board__(board):
            raise InvalidShipPlacementException()
        self.defence_board = board

    def add_offence_shot(self, shot, result, ship_sunk, sunken_ship_type):
        shot_x, shot_y = self.__shot_to_xy__(shot)
        shot_idx = self.__xy_to_idx__(shot_x, shot_y)

        # Something wrong
        assert self.offence_board[shot_idx] != GameStatus.MARKER_MISS \
               and self.offence_board[shot_idx] != GameStatus.MARKER_HIT

        self.offence_shot_log.append(shot)
        self.offence_board[shot_idx] = result

        if result == GameStatus.MARKER_HIT:
            self.offence_hp_sum -= 1
            if ship_sunk:
                self.offence_enemy_sink_log.append((self.offence_turn, sunken_ship_type))
                self.offence_ships_alive.remove(sunken_ship_type)
            if self.offence_hp_sum == 0:
                assert len(self.offence_ships_alive) == 0  # Something wrong
                self.offence_win = True
                self.defence_win = False
                self.game_over = True

        self.offence_turn += 1

    def add_defence_shot(self, shot):
        shot_x, shot_y = self.__shot_to_xy__(shot)
        shot_idx = self.__xy_to_idx__(shot_x, shot_y)

        if self.defence_board[shot_idx] == GameStatus.MARKER_MISS \
                or self.defence_board[shot_idx] == GameStatus.MARKER_HIT:
            raise InvalidShotException(f"You have already called '{shot}'!")

        # Valid shot
        self.defence_shot_log.append(shot)

        if self.defence_board[shot_idx] == GameStatus.MARKER_EMPTY:
            # Missed
            self.defence_board[shot_idx] = GameStatus.MARKER_MISS
            return GameStatus.MARKER_MISS, False, None

        # Hit
        ship = self.defence_board[shot_idx]
        assert self.defence_ships_hp[ship] != 0  # Something wrong

        self.defence_board[shot_idx] = GameStatus.MARKER_HIT
        self.defence_ships_hp[ship] -= 1
        self.defence_hp_sum -= 1
        ship_sunk = (self.defence_ships_hp[ship] == 0)
        sunken_ship_type = None
        if ship_sunk:
            sunken_ship_type = ship

        if self.defence_hp_sum == 0:
            self.defence_win = False
            self.offence_win = True
            self.game_over = True

        return GameStatus.MARKER_HIT, ship_sunk, sunken_ship_type

    def get_last_shot(self):
        if len(self.offence_shot_log) > 0:
            last_shot = self.offence_shot_log[-1]
            last_shot_idx = self.__shot_to_idx__(last_shot)
            last_shot_result = self.offence_board[last_shot_idx]
            last_sunken_ship = None
            if len(self.offence_enemy_sink_log) > 0 and self.offence_enemy_sink_log[-1][0] == self.offence_turn - 1:
                last_sunken_ship = self.offence_enemy_sink_log[-1][1]

            return last_shot, last_shot_result, last_sunken_ship
        else:
            return None, None, None

    def get_surrounding_shots(self, shot):
        base_x, base_y = self.__shot_to_xy__(shot)
        shots = []
        for delta_x, delta_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x = base_x + delta_x
            new_y = base_y + delta_y
            if new_x < 0 or new_x >= self.size_x or new_y < 0 or new_y >= self.size_y:
                continue
            shots.append(self.__xy_to_shot__(new_x, new_y))
        return shots

    def __verify_board__(self, board):
        # TODO implement
        return True

    def __xy_to_idx__(self, x, y):
        if x >= self.size_x or y >= self.size_y:
            raise InvalidShotException(f"Invalid coordinate, ({x}, {y})")
        return x * self.size_y + y

    def __idx_to_xy__(self, idx):
        x = int(idx / self.size_y)
        y = idx % self.size_y
        return x, y

    def __shot_to_xy__(self, shot: str):
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

    def __xy_to_shot__(self, x, y):
        if x >= self.size_x or y >= self.size_y:
            raise InvalidShotException(f"Invalid coordinate, ({x}, {y})")
        return f"{chr(ord('A') + x)}{y + 1}"

    def __idx_to_shot__(self, idx):
        x, y = self.__idx_to_xy__(idx)
        return self.__xy_to_shot__(x, y)

    def __shot_to_idx__(self, shot):
        x, y = self.__shot_to_xy__(shot)
        return self.__xy_to_idx__(x, y)

    @staticmethod
    def __board_to_str__(board):
        return ''.join(board)
