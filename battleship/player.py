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


class RandomPlayer(Player):
    def __init__(self):
        super().__init__()
        self.__name__ = "RandomPlayer"

    def shoot(self):
        self.game_status.print_offence_board()
        shot = chr(random.randint(0, 9) + ord('A')) + f'{random.randint(1, 10)}'
        print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot

