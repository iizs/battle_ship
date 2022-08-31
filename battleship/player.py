import logging
import abc
import random

logger = logging.getLogger(__name__)


class Player:
    def __init__(self):
        self.name = None
        self.__name__ = "Player"

    @abc.abstractmethod
    def shoot(self, player_board):
        pass

    def game_end(self, player_board):
        Player.print_board(player_board)

    @staticmethod
    def print_board(board):
        # TODO make 10 as constant
        for x in range(10):
            print(' '.join(board[x * 10:(x + 1) * 10]))


class HumanPlayer(Player):
    def __init__(self):
        super().__init__()
        self.__name__ = "HumanPlayer"

    def shoot(self, player_board):
        Player.print_board(player_board)
        shot = input('A~J / 0~9 > ')
        # TODO input validation
        return shot


class RandomPlayer(Player):
    def __init__(self):
        super().__init__()
        self.__name__ = "RandomPlayer"

    def shoot(self, player_board):
        Player.print_board(player_board)
        shot = chr(random.randint(0, 9) + ord('A')) + chr(random.randint(0, 9) + ord('0'))
        print(f'Shoot at {shot}')
        return shot

