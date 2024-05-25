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
    def __init__(self):
        super().__init__(
            (880, 880),
            10,
            color="pink",
            mask_color="black"
        )

    def update(self):
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
    def __init__(self):
        super().__init__(
            (840, 260),
            10,
            color="gray",
            mask_color="black"
        )

    def update(self):
        self.surface.blit(self.mask_surface, (0, 0))


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

        board_area = BoardArea()
        statistics_area = StatisticsArea()
        message_area = MessageArea()

        while True:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            shot = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise QuitGameException()

            if shot is not None:
                try:
                    shot_result, ship_sunk = self.npc_game_status.add_defence_shot(shot)
                    self.player_game_status.add_offence_shot(shot, shot_result, ship_sunk)
                except InvalidShotException as e:
                    logger.warning(e)

            # TODO draw screen
            self.main_surface.fill("black")

            board_area.update()
            self.main_surface.blit(board_area.surface, (100, 100))

            statistics_area.update()
            self.main_surface.blit(statistics_area.surface, (1000, 100))

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
