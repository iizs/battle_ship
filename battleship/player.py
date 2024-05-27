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

    @abc.abstractmethod
    def reset(self):
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
                    pos_y = random.randint(0, self.game_status.size_y - GameStatus.SHIPS_AND_SIZES[ship])

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
                    pos_x = random.randint(0, self.game_status.size_x - GameStatus.SHIPS_AND_SIZES[ship])
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

    def reset(self):
        pass


class RandomPlayer(Player):
    def __init__(self, console_io=False):
        super().__init__(console_io=console_io)
        self.__name__ = "RandomPlayer"
        self.shot_candidates = None
        self.reset()

    def shoot(self):
        shot = self.shot_candidates.pop(0)
        if self.console_io:
            print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot

    def reset(self):
        self.shot_candidates = []
        for x in range(10):
            for y in range(10):
                self.shot_candidates.append(f"{chr(x + ord('A'))}{y + 1}")
        random.shuffle(self.shot_candidates)


class SequentialPlayer(Player):
    def __init__(self, console_io=False):
        super().__init__(console_io=console_io)
        self.__name__ = "SequentialPlayer"
        self.shot_candidates = None
        self.reset()

    def shoot(self):
        shot = self.shot_candidates.pop(0)
        if self.console_io:
            print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot

    def reset(self):
        self.shot_candidates = []
        for x in range(10):
            for y in range(10):
                self.shot_candidates.append(f"{chr(x + ord('A'))}{y + 1}")
