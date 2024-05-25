import logging
import abc
import random
from .game_status import GameStatus

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, console_io=False):
        self.name = None
        self.__name__ = "Player"
        self.game_status = GameStatus(10, 10)  # default
        self.console_io = console_io

    @abc.abstractmethod
    def shoot(self):
        pass

    def place_ships(self):
        board = [GameStatus.MARKER_EMPTY] * (self.game_status.size_x * self.game_status.size_y)

        for ship in GameStatus.SHIPS_AND_SIZES:
            ship_placed = False
            while not ship_placed:
                direction = random.randint(0, 1)
                if direction == 0:
                    # Horizontal (same pos_x)
                    pos_x = random.randint(0, self.game_status.size_x - 1)
                    pos_y = random.randint(0, self.game_status.size_y - 1 - GameStatus.SHIPS_AND_SIZES[ship])

                    can_be_placed = True
                    for l in range(GameStatus.SHIPS_AND_SIZES[ship]):
                        if board[self.game_status.__xy_to_idx__(pos_x, pos_y + l)] != GameStatus.MARKER_EMPTY:
                            can_be_placed = False
                            break
                    if can_be_placed:
                        for l in range(GameStatus.SHIPS_AND_SIZES[ship]):
                            board[self.game_status.__xy_to_idx__(pos_x, pos_y + l)] = ship
                        ship_placed = True

                else:  # direction = 1
                    # Vertical (same pos_y)
                    pos_x = random.randint(0, self.game_status.size_x - 1 - GameStatus.SHIPS_AND_SIZES[ship])
                    pos_y = random.randint(0, self.game_status.size_y - 1)

                    can_be_placed = True
                    for l in range(GameStatus.SHIPS_AND_SIZES[ship]):
                        if board[self.game_status.__xy_to_idx__(pos_x + l, pos_y)] != GameStatus.MARKER_EMPTY:
                            can_be_placed = False
                            break
                    if can_be_placed:
                        for l in range(GameStatus.SHIPS_AND_SIZES[ship]):
                            board[self.game_status.__xy_to_idx__(pos_x + l, pos_y)] = ship
                        ship_placed = True

        return board

    def update_game_status(self, game_status: GameStatus):
        self.game_status = game_status


class HumanPlayer(Player):
    def __init__(self, console_io=False):
        super().__init__(console_io=console_io)
        self.__name__ = "HumanPlayer"

    def shoot(self):
        shot = input(f'Turn {self.game_status.offence_turn}: A~J / 0~9 > ')
        return shot


class RandomPlayer(Player):
    def __init__(self, console_io=False):
        super().__init__(console_io=console_io)
        self.__name__ = "RandomPlayer"

    def shoot(self):
        shot = chr(random.randint(0, 9) + ord('A')) + f'{random.randint(1, 10)}'
        if self.console_io:
            print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot
