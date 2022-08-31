import logging

logger = logging.getLogger(__name__)


class SingleGame:
    SIZE_X = 10
    SIZE_Y = 10

    def __init__(self, player):
        self.game_board = ['.' for i in range(SingleGame.SIZE_X * SingleGame.SIZE_Y)]
        self.player_board = ['.' for i in range(SingleGame.SIZE_X * SingleGame.SIZE_Y)]
        self.total_ship_health = 17
        self.game_over = False
        self.__place_ships__()
        self.player = player

    def __place_ships__(self):
        self.game_board[0] = '1'
        self.game_board[1] = '1'
        self.game_board[2] = '1'
        self.game_board[3] = '1'
        self.game_board[4] = '1'

        self.game_board[19] = '2'
        self.game_board[29] = '2'
        self.game_board[39] = '2'

        self.game_board[77] = '3'
        self.game_board[78] = '3'
        self.game_board[79] = '3'

        self.game_board[55] = '4'
        self.game_board[65] = '4'
        self.game_board[75] = '4'
        self.game_board[85] = '4'

        self.game_board[91] = '5'
        self.game_board[92] = '5'

    def print_game_board(self):
        for x in range(SingleGame.SIZE_X):
            print(' '.join(self.game_board[x * SingleGame.SIZE_Y:(x + 1) * SingleGame.SIZE_Y]))

    @staticmethod
    def x_y_to_idx(x, y):
        return x * SingleGame.SIZE_Y + y

    def __update_status__(self, shot):
        x = ord(shot[0]) - ord('A')
        y = int(shot[1])
        idx = SingleGame.x_y_to_idx(x, y)
        if self.game_board[idx] == '.':
            self.game_board[idx] = '_'
            self.player_board[idx] = '_'
        elif self.game_board[idx] == '_' or self.game_board[idx] == 'X':
            pass
        else:
            self.game_board[idx] = 'X'
            self.player_board[idx] = 'X'
            self.total_ship_health -= 1
            if self.total_ship_health == 0:
                self.game_over = True

    def start(self):
        while not self.game_over:
            shot_location = self.player.shoot(self.player_board)
            self.__update_status__(shot_location)
        self.player.game_end(self.player_board)
