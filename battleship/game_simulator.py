import logging
import pygame
import math
from .exception import *
from .game_status import GameStatus
from .player import RandomPlayer, HumanPlayer

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    WIDTH = 660
    HEIGHT = 660
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

    def draw_target(self, x, y, mark):
        rect = pygame.Rect(
            BoardArea.MARGIN + x * (self.gap_between_location + self.target_width),
            BoardArea.MARGIN + y * (self.gap_between_location + self.target_height),
            self.target_width,
            self.target_height
        )

        if mark == GameStatus.MARKER_HIT:
            pygame.draw.rect(self.surface, 'red', rect)
        elif mark == GameStatus.MARKER_MISS:
            pygame.draw.rect(self.surface, 'blue', rect)
        else:
            pygame.draw.rect(self.surface, 'gray', rect)

    def update(self, game_status):
        self.surface.fill(BoardArea.BACKGROUND_COLOR)
        for x in range(1, self.map_size_x + 1):
            for y in range(1, self.map_size_y + 1):
                self.draw_target(x, y, game_status.offence_board[(y - 1) * self.map_size_y + x - 1])

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

    def convert_pos_to_board_coord(self, offset, pos):
        x = pos[0] - (offset[0] + BoardArea.MARGIN + self.gap_between_location + self.target_width)
        y = pos[1] - (offset[1] + BoardArea.MARGIN + self.gap_between_location + self.target_height)
        if x < 0 or x > (self.gap_between_location + self.target_width) * self.map_size_x:
            return None
        if y < 0 or y > (self.gap_between_location + self.target_height) * self.map_size_y:
            return None

        coord_x = int(x / (self.gap_between_location + self.target_width)) + 1
        coord_y = int(y / (self.gap_between_location + self.target_height)) + 1
        return f"{chr(coord_y + ord('A') - 1)}{coord_x}"


class StatisticsArea(Area):
    BACKGROUND_COLOR = 'gray'
    MARGIN = 20
    FONT_NAME = 'Lucida Console'
    FONT_SIZE = 20
    LINE_WIDTH = 4
    SUB_LINE_WIDTH = 1
    BAR_MARGIN = 2

    AREA_WIDTH = 1040
    AREA_HEIGHT = 880

    def __init__(self):
        super().__init__(
            (StatisticsArea.AREA_WIDTH, StatisticsArea.AREA_HEIGHT),
            10,
            color=StatisticsArea.BACKGROUND_COLOR,
            mask_color="black"
        )

        self.axis_font = pygame.font.SysFont(StatisticsArea.FONT_NAME, StatisticsArea.FONT_SIZE)
        self.bar_min_index = 16

    def update(self, values):
        self.surface.fill(StatisticsArea.BACKGROUND_COLOR)

        reference_text = self.axis_font.render("1,000", True, 'black')

        bar_base_x = StatisticsArea.MARGIN + reference_text.get_width() + StatisticsArea.LINE_WIDTH
        bar_base_y = StatisticsArea.AREA_HEIGHT \
            - reference_text.get_height() - StatisticsArea.MARGIN - StatisticsArea.LINE_WIDTH / 2
        num_bars = len(values) - self.bar_min_index + 1
        bar_width = math.floor(
            (StatisticsArea.AREA_WIDTH - 2 * StatisticsArea.MARGIN
             - reference_text.get_width() - StatisticsArea.LINE_WIDTH) / num_bars
        )

        # X-axis
        pygame.draw.line(
            self.surface, 'black',
            (StatisticsArea.MARGIN + reference_text.get_width(),
             StatisticsArea.AREA_HEIGHT - reference_text.get_height() - StatisticsArea.MARGIN),
            (StatisticsArea.AREA_WIDTH - StatisticsArea.MARGIN,
             StatisticsArea.AREA_HEIGHT - reference_text.get_height() - StatisticsArea.MARGIN),
            width=StatisticsArea.LINE_WIDTH)

        x_index = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        for i in x_index:
            text = self.axis_font.render(f"{i}", True, 'black')
            self.surface.blit(
                text,
                (bar_base_x + (i - 15) * bar_width - text.get_width(), bar_base_y + StatisticsArea.LINE_WIDTH)
            )

        # Y-Axis
        pygame.draw.line(
            self.surface, 'black',
            (StatisticsArea.MARGIN + reference_text.get_width(),
             StatisticsArea.MARGIN),
            (StatisticsArea.MARGIN + reference_text.get_width(),
             StatisticsArea.AREA_HEIGHT - reference_text.get_height() - StatisticsArea.MARGIN),
            width=StatisticsArea.LINE_WIDTH)

        y_max = 200
        y_index = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
        y_axis_length = StatisticsArea.AREA_HEIGHT - reference_text.get_height() - 2 * StatisticsArea.MARGIN
        for i in y_index:
            text = self.axis_font.render(f"{i}", True, 'black')
            self.surface.blit(
                text,
                (bar_base_x - text.get_width() - StatisticsArea.LINE_WIDTH - StatisticsArea.BAR_MARGIN,
                 bar_base_y - y_axis_length / y_max * i - text.get_height() / 2 + StatisticsArea.LINE_WIDTH / 2)
            )
            pygame.draw.line(
                self.surface, 'black',
                (StatisticsArea.MARGIN + reference_text.get_width(),
                 bar_base_y - y_axis_length / y_max * i + StatisticsArea.LINE_WIDTH / 2),
                (StatisticsArea.AREA_WIDTH - StatisticsArea.MARGIN,
                 bar_base_y - y_axis_length / y_max * i + StatisticsArea.LINE_WIDTH / 2),
                width=StatisticsArea.SUB_LINE_WIDTH)

        # Draw bars
        for i in range(self.bar_min_index, len(values)):
            bar_height = y_axis_length / y_max * values[i]
            rect = pygame.Rect(
                bar_base_x + (i - self.bar_min_index) * bar_width + StatisticsArea.BAR_MARGIN,
                bar_base_y - bar_height + StatisticsArea.LINE_WIDTH / 2,
                bar_width - StatisticsArea.BAR_MARGIN,
                bar_height
            )
            pygame.draw.rect(self.surface, 'red', rect)

        self.surface.blit(self.mask_surface, (0, 0))


class MessageArea(Area):
    BACKGROUND_COLOR = 'gray'
    MARGIN = 20
    FONT_NAME = 'Lucida Console'
    FONT_SIZE = 16
    LINE_SPACING = 8

    def __init__(self):
        super().__init__(
            (660, 200),
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
        self.game_num = 0
        self.win_statistics = [0] * 100

        # pygame variables
        self.main_surface = None
        self.clock = None

        self.statistics_area = None
        self.message_area = None

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
        self.player.reset()
        self.player.update_game_status(self.player_game_status)

        board_area = BoardArea(SingleOffenceGameSimulator.SIZE_X, SingleOffenceGameSimulator.SIZE_Y)

        shot_num = 1
        shot = None
        left_click = None
        # self.message_area.append_text(f"Turn {shot_num}")
        while not self.player_game_status.game_over:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise QuitGameException()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        left_click = event.pos

            if left_click is not None:
                shot = board_area.convert_pos_to_board_coord((100, 100), left_click)
                # if shot is not None:
                #     self.message_area.append_text(f"You called '{shot}'")
                left_click = None

            if not isinstance(self.player, HumanPlayer):
                shot = self.player.shoot()
                # self.message_area.append_text(f"You called '{shot}'")

            if shot is not None:
                try:
                    shot_result, ship_sunk, sunken_ship_type = self.npc_game_status.add_defence_shot(shot)
                    self.player_game_status.add_offence_shot(shot, shot_result, ship_sunk, sunken_ship_type)

                    if self.player_game_status.game_over:
                        self.message_area.append_text(f"Game {self.game_num}: You win in {shot_num} turns!")
                        self.win_statistics[shot_num - 1] += 1
                    else:
                        shot_num += 1
                        # self.message_area.append_text(f"Turn {shot_num}")
                except InvalidShotException as e:
                    logger.warning(e)
                    self.message_area.append_text(str(e))
                shot = None

            # Draw screen
            self.main_surface.fill("black")

            board_area.update(self.player_game_status)
            self.main_surface.blit(board_area.surface, (100, 100))

            self.statistics_area.update(self.win_statistics)
            self.main_surface.blit(self.statistics_area.surface, (780, 100))

            self.message_area.update()
            self.main_surface.blit(self.message_area.surface, (100, 780))

            pygame.display.flip()

    def start(self):
        pygame.init()

        logger.info('SingleOffenceGameSimulator starts.')
        logger.info(f"{self.player.__class__.__name__}")
        logger.info(f"{self.num_simulation} Games")

        self.main_surface = pygame.display.set_mode(SingleOffenceGameSimulator.SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        self.statistics_area = StatisticsArea()
        self.message_area = MessageArea()

        SingleOffenceGameSimulator.wait_for_press_any_key()

        for n in range(self.num_simulation):
            self.game_num += 1
            # self.message_area.append_text(f"Game {self.game_num}")
            self.run_simulation()
            if isinstance(self.player, HumanPlayer):
                SingleOffenceGameSimulator.wait_for_press_any_key()

        logger.info(self.win_statistics)
        if not isinstance(self.player, HumanPlayer):
            SingleOffenceGameSimulator.wait_for_press_any_key()

        logger.info('SingleOffenceGameSimulator ends.')
