import logging
import abc
import random
from .game_status import GameStatus
from .exception import InvalidShotException

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, console_io=False):
        self.name = None
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

    def shoot(self):
        shot = input(f'Turn {self.game_status.offence_turn}: A~J / 0~9 > ')
        return shot

    def reset(self):
        pass


class SequentialPlayer(Player):
    def __init__(self, console_io=False):
        super().__init__(console_io=console_io)
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


class RandomPlayer(SequentialPlayer):
    def __init__(self, console_io=False):
        super().__init__(console_io=console_io)

    def reset(self):
        super().reset()
        random.shuffle(self.shot_candidates)


class HuntAndTargetPlayer(RandomPlayer):
    def __init__(self, console_io=False):
        self.targets = None
        super().__init__(console_io=console_io)

    def shoot(self):
        last_shot, last_shot_result, last_sunken_ship = self.game_status.get_last_shot()
        if last_shot_result == GameStatus.MARKER_HIT:
            targets = self.game_status.get_surrounding_shots(last_shot)
            for shot in targets:
                if shot in self.shot_candidates and shot not in self.targets:
                    self.targets.append(shot)

        if len(self.targets) == 0:
            shot = self.shot_candidates.pop(0)
        else:
            shot = self.targets.pop(0)
            self.shot_candidates.remove(shot)
        if self.console_io:
            print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot

    def reset(self):
        super().reset()
        self.targets = []


class ProbabilityPlayer(SequentialPlayer):
    def __init__(self, console_io=False):
        self.sunken_ships_with_active_hits = []
        self.active_hits_idx = []
        self.alive_ships = None
        super().__init__(console_io=console_io)

    def get_max_hunting_probability_shot(self):
        prob = [0] * (self.game_status.size_x * self.game_status.size_y)
        for ship in self.alive_ships:
            ship_size = self.game_status.SHIPS_AND_SIZES[ship]
            for idx in range(self.game_status.size_x * self.game_status.size_y):
                if self.game_status.offence_board[idx] != GameStatus.MARKER_EMPTY:
                    continue
                base_x, base_y = self.game_status.__idx_to_xy__(idx)

                # Test Horizontal Placement
                horizontal_available = True
                for delta in range(1, ship_size):
                    try:
                        test_idx = self.game_status.__xy_to_idx__(base_x, base_y + delta)
                    except InvalidShotException:
                        horizontal_available = False
                        break

                    if self.game_status.offence_board[test_idx] != GameStatus.MARKER_EMPTY:
                        horizontal_available = False
                        break

                if horizontal_available:
                    for delta in range(0, ship_size):
                        prob_idx = self.game_status.__xy_to_idx__(base_x, base_y + delta)
                        prob[prob_idx] += 1

                # Test Vertical Placement
                vertical_available = True
                for delta in range(1, ship_size):
                    try:
                        test_idx = self.game_status.__xy_to_idx__(base_x + delta, base_y)
                    except InvalidShotException:
                        vertical_available = False
                        break
                    if self.game_status.offence_board[test_idx] != GameStatus.MARKER_EMPTY:
                        vertical_available = False
                        break

                if vertical_available:
                    for delta in range(0, ship_size):
                        prob_idx = self.game_status.__xy_to_idx__(base_x + delta, base_y)
                        prob[prob_idx] += 1
        max_prob = 0
        max_prob_idx = 0
        for idx in range(self.game_status.size_x * self.game_status.size_y):
            if prob[idx] > max_prob:
                max_prob_idx = idx
                max_prob = prob[idx]

        return self.game_status.__idx_to_shot__(max_prob_idx)

    def get_max_targeting_probability_shot(self):
        prob = [0] * (self.game_status.size_x * self.game_status.size_y)
        for ship in self.alive_ships:
            ship_size = self.game_status.SHIPS_AND_SIZES[ship]
            for idx in range(self.game_status.size_x * self.game_status.size_y):
                base_x, base_y = self.game_status.__idx_to_xy__(idx)

                # Test Horizontal Placement
                horizontal_available = True
                overlaps_with_active_hits = False
                for delta in range(0, ship_size):
                    try:
                        test_idx = self.game_status.__xy_to_idx__(base_x, base_y + delta)
                    except InvalidShotException:
                        horizontal_available = False
                        break

                    marker = self.game_status.offence_board[test_idx]
                    if marker == GameStatus.MARKER_MISS:
                        horizontal_available = False
                        break
                    elif marker == GameStatus.MARKER_HIT:
                        if test_idx in self.active_hits_idx:
                            overlaps_with_active_hits = True
                        else:
                            horizontal_available = False
                            break

                if horizontal_available and overlaps_with_active_hits:
                    for delta in range(0, ship_size):
                        prob_idx = self.game_status.__xy_to_idx__(base_x, base_y + delta)
                        if self.game_status.offence_board[prob_idx] == GameStatus.MARKER_EMPTY:
                            prob[prob_idx] += 1

                # Test Vertical Placement
                vertical_available = True
                overlaps_with_active_hits = False
                for delta in range(0, ship_size):
                    try:
                        test_idx = self.game_status.__xy_to_idx__(base_x + delta, base_y)
                    except InvalidShotException:
                        vertical_available = False
                        break

                    marker = self.game_status.offence_board[test_idx]
                    if marker == GameStatus.MARKER_MISS:
                        vertical_available = False
                        break
                    elif marker == GameStatus.MARKER_HIT:
                        if test_idx in self.active_hits_idx:
                            overlaps_with_active_hits = True
                        else:
                            vertical_available = False
                            break

                if vertical_available and overlaps_with_active_hits:
                    for delta in range(0, ship_size):
                        prob_idx = self.game_status.__xy_to_idx__(base_x + delta, base_y)
                        if self.game_status.offence_board[prob_idx] == GameStatus.MARKER_EMPTY:
                            prob[prob_idx] += 1
        max_prob = 0
        max_prob_idx = 0
        for idx in range(self.game_status.size_x * self.game_status.size_y):
            if prob[idx] > max_prob:
                max_prob_idx = idx
                max_prob = prob[idx]

        return self.game_status.__idx_to_shot__(max_prob_idx)

    def shoot(self):
        last_shot, last_shot_result, last_sunken_ship = self.game_status.get_last_shot()
        if last_shot_result == GameStatus.MARKER_HIT:
            self.active_hits_idx.append(self.game_status.__shot_to_idx__(last_shot))
            if last_sunken_ship is not None:
                self.alive_ships.remove(last_sunken_ship)
                self.sunken_ships_with_active_hits.append(last_sunken_ship)
                sum_length_sunken_ships = 0
                for ship in self.sunken_ships_with_active_hits:
                    sum_length_sunken_ships += GameStatus.SHIPS_AND_SIZES[ship]
                if sum_length_sunken_ships == len(self.active_hits_idx):
                    self.active_hits_idx = []
                    self.sunken_ships_with_active_hits = []

        if len(self.active_hits_idx) == 0:
            shot = self.get_max_hunting_probability_shot()
            self.shot_candidates.remove(shot)
        else:
            shot = self.get_max_targeting_probability_shot()
            self.shot_candidates.remove(shot)
        if self.console_io:
            print(f'Turn {self.game_status.offence_turn}: Shoot at {shot}')
        return shot

    def reset(self):
        super().reset()
        self.active_hits_idx = []
        self.sunken_ships_with_active_hits = []
        self.alive_ships = [
            GameStatus.MARKER_PATROL_BOAT,
            GameStatus.MARKER_SUBMARINE,
            GameStatus.MARKER_DESTROYER,
            GameStatus.MARKER_BATTLESHIP,
            GameStatus.MARKER_CARRIER,
        ]
