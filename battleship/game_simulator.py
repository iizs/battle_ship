import logging
import pygame
from .exception import *
from .game_status import GameStatus
from .player import RandomPlayer

logger = logging.getLogger(__name__)


class Area:
    TEMP_COLOR = "pink"

    def __init__(self, size, border_radius, color='white', mask_color='black'):
        self.mask_surface = Area.make_round_border_mask_surface(size, mask_color, border_radius)
        self.surface = pygame.Surface(size)
        self.surface.fill(color)

    @staticmethod
    def make_round_border_mask_surface(size, mask_color, border_radius):
        shape1 = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(shape1, Area.TEMP_COLOR, (0, 0, size[0], size[1]), )
        shape2 = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(shape2, Area.TEMP_COLOR, (0, 0, size[0], size[1]), border_radius=border_radius)
        mask1 = pygame.mask.from_surface(shape1)
        mask2 = pygame.mask.from_surface(shape2)

        mask2.invert()
        subtract_mask = mask1.overlap_mask(mask2, (0, 0))

        return subtract_mask.to_surface(setcolor=mask_color, unsetcolor=(0, 0, 0, 0))


class BoardArea(Area):
    BACKGROUND_COLOR = 'pink'
    WIDTH = 880
    HEIGHT = 880
    MARGIN = 10
    FONT_NAME = 'Lucida Console'
    FONT_SIZE = 36

    def __init__(self, map_size_x, map_size_y, gap=5):
        super().__init__(
            (BoardArea.WIDTH, BoardArea.HEIGHT),
            10,
            color=BoardArea.BACKGROUND_COLOR,
            mask_color="black"
        )
        self.map_size_x = map_size_x
        self.map_size_y = map_size_y
        self.gap_between_location = gap

        self.target_width = int(
            (BoardArea.WIDTH - 2 * BoardArea.MARGIN - self.map_size_x * self.gap_between_location)
            / (1 + self.map_size_x)
        )
        self.target_height = int(
            (BoardArea.HEIGHT - 2 * BoardArea.MARGIN - self.map_size_y * self.gap_between_location)
            / (1 + self.map_size_y)
        )
        self.target_font = pygame.font.SysFont(BoardArea.FONT_NAME, BoardArea.FONT_SIZE)

    def draw_target(self, x, y):
        rect = pygame.Rect(
            BoardArea.MARGIN + x * (self.gap_between_location + self.target_width),
            BoardArea.MARGIN + y * (self.gap_between_location + self.target_height),
            self.target_width,
            self.target_height
        )
        pygame.draw.rect(self.surface, 'gray', rect)

    def update(self):
        self.surface.fill(BoardArea.BACKGROUND_COLOR)
        for x in range(1, self.map_size_x + 1):
            for y in range(1, self.map_size_y + 1):
                self.draw_target(x, y)

        # Print X coordinates
        for x in range(1, self.map_size_x + 1):
            x_text = self.target_font.render(f"{x}", True, 'black')
            x_text_width = x_text.get_width()
            x_text_height = x_text.get_height()
            x_text_y = BoardArea.MARGIN + (self.target_height - x_text_height) / 2
            x_text_x = BoardArea.MARGIN + x * (self.gap_between_location + self.target_width) + (self.target_width - x_text_width) / 2
            self.surface.blit(x_text, (x_text_x, x_text_y))

        # Print Y coordinates
        for y in range(1, self.map_size_y + 1):
            y_text = self.target_font.render(f"{chr(y + ord('A') - 1)}", True, 'black')
            y_text_width = y_text.get_width()
            y_text_height = y_text.get_height()

            y_text_y = BoardArea.MARGIN + y * (self.gap_between_location + self.target_height) + (
                        self.target_height - y_text_height) / 2
            y_text_x = BoardArea.MARGIN + (self.target_width - y_text_width) / 2
            self.surface.blit(y_text, (y_text_x, y_text_y))

        self.surface.blit(self.mask_surface, (0, 0))


class StatisticsArea(Area):
    def __init__(self):
        super().__init__(
            (840, 600),
            10,
            color="pink",
            mask_color="black"
        )

    def update(self):
        self.surface.blit(self.mask_surface, (0, 0))


class MessageArea(Area):
    BACKGROUND_COLOR = 'gray'
    MARGIN = 10
    FONT_NAME = 'Lucida Console'
    FONT_SIZE = 16
    LINE_SPACING = 8

    def __init__(self):
        super().__init__(
            (840, 260),
            10,
            color=MessageArea.BACKGROUND_COLOR,
            mask_color="black"
        )
        self.messages = []
        self.message_font = pygame.font.SysFont(MessageArea.FONT_NAME, MessageArea.FONT_SIZE)

    def update(self):
        self.surface.fill(MessageArea.BACKGROUND_COLOR)
        line_x = MessageArea.MARGIN
        line_y = self.surface.get_size()[1]
        for line in self.messages:
            text = self.message_font.render(line, True, 'black')
            line_y -= text.get_height() + MessageArea.LINE_SPACING
            self.surface.blit(text, (line_x, line_y))
            if line_y < 0:
                break
        self.surface.blit(self.mask_surface, (0, 0))

    def append_text(self, text):
        self.messages.insert(0, text)


class SingleOffenceGameSimulator:
    SIZE_X = 10
    SIZE_Y = 10

    SCREEN_SIZE = (1920, 1080)

    def __init__(self, player, num_simulation=10):
        self.player = player
        self.npc_player = RandomPlayer()
        self.player_game_status = None
        self.npc_game_status = None
        self.num_simulation = num_simulation

        # pygame variables
        self.main_surface = None
        self.clock = None

    @staticmethod
    def wait_for_press_any_key():
        pygame.display.flip()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise QuitGameException()
                if event.type == pygame.KEYDOWN:
                    wait = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    wait = False

    def run_simulation(self):
        self.player_game_status = GameStatus(SingleOffenceGameSimulator.SIZE_X, SingleOffenceGameSimulator.SIZE_Y)
        self.npc_game_status = GameStatus(SingleOffenceGameSimulator.SIZE_X, SingleOffenceGameSimulator.SIZE_Y)
        self.npc_player.update_game_status(self.npc_game_status)
        self.npc_game_status.set_defence_board(self.npc_player.place_ships())
        self.player.update_game_status(self.player_game_status)

        board_area = BoardArea(SingleOffenceGameSimulator.SIZE_X, SingleOffenceGameSimulator.SIZE_Y)
        statistics_area = StatisticsArea()
        message_area = MessageArea()

        msg = None
        while True:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            shot = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise QuitGameException()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    msg = str(event)

            if shot is not None:
                try:
                    shot_result, ship_sunk = self.npc_game_status.add_defence_shot(shot)
                    self.player_game_status.add_offence_shot(shot, shot_result, ship_sunk)
                except InvalidShotException as e:
                    logger.warning(e)

            # Draw screen
            self.main_surface.fill("black")

            board_area.update()
            self.main_surface.blit(board_area.surface, (100, 100))

            statistics_area.update()
            self.main_surface.blit(statistics_area.surface, (1000, 100))

            if msg is not None:
                message_area.append_text(msg)
                msg = None
            message_area.update()
            self.main_surface.blit(message_area.surface, (1000, 720))

            pygame.display.flip()

        self.player.update_game_status(self.player_game_status)

    def start(self):
        pygame.init()
        self.main_surface = pygame.display.set_mode(SingleOffenceGameSimulator.SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        SingleOffenceGameSimulator.wait_for_press_any_key()

        for n in range(self.num_simulation):
            self.run_simulation()

        SingleOffenceGameSimulator.wait_for_press_any_key()
