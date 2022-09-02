import logging
import abc
import random
from .game import GameStatus

logger = logging.getLogger(__name__)


class Player:
    def __init__(self):
        self.name = None
        self.__name__ = "Player"
        self.game_status = GameStatus(10, 10)  # default

    @abc.abstractmethod
    def shoot(self):
        pass

    @abc.abstractmethod
    def place_ships(self):
        pass

    def update_game_status(self, game_status: GameStatus):
        self.game_status = game_status
        if self.game_status.game_over:
            game_status.print_offence_board()


class HumanPlayer(Player):
    def __init__(self):
        super().__init__()
        self.__name__ = "HumanPlayer"

    def shoot(self):
        self.game_status.print_offence_board()
        shot = input(f'Turn {self.game_status.offence_turn}: A~J / 0~9 > ')
        return shot

    def place_ships(self):
        return None


class RandomPlayer(Player):
    def __init__(self):
        super().__init__()
        self.__name__ = "RandomPlayer"

    def shoot(self):
        self.game_status.print_offence_board()
        shot = chr(random.randint(0, 9) + ord('A')) + f'{random.randint(1, 10)}'
        print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot

    def place_ships(self):
        board = [GameStatus.MARKER_EMPTY] * (self.game_status.size_x * self.game_status.size_y)
        board[0] = GameStatus.MARKER_CARRIER
        board[1] = GameStatus.MARKER_CARRIER
        board[2] = GameStatus.MARKER_CARRIER
        board[3] = GameStatus.MARKER_CARRIER
        board[4] = GameStatus.MARKER_CARRIER

        board[19] = GameStatus.MARKER_DESTROYER
        board[29] = GameStatus.MARKER_DESTROYER
        board[39] = GameStatus.MARKER_DESTROYER

        board[77] = GameStatus.MARKER_SUBMARINE
        board[78] = GameStatus.MARKER_SUBMARINE
        board[79] = GameStatus.MARKER_SUBMARINE

        board[55] = GameStatus.MARKER_BATTLESHIP
        board[65] = GameStatus.MARKER_BATTLESHIP
        board[75] = GameStatus.MARKER_BATTLESHIP
        board[85] = GameStatus.MARKER_BATTLESHIP

        board[91] = GameStatus.MARKER_PATROL_BOAT
        board[92] = GameStatus.MARKER_PATROL_BOAT

        return board

