import numpy as np
import pygame
import gymnasium as gym
from gymnasium import spaces
from battleship.game_status import GameStatus
from battleship.game_simulator import BoardArea
from battleship.player import RandomPlayer
from battleship.exception import InvalidShotException


class BattleshipEnv(gym.Env):
    """
    ## Action Space
    The action shape is `(1,)` in the range `{0, 99}` indicating x, y coord of a shot

    ## Observation Space
    `Box(-1, 1, (10, 10), np.int8)`
    -1 means a miss, 0 means empty, and 1 means a hit

    ## Rewards
    * invalid shot: -100
    * hit: 10
    * miss: 0
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    MARKER_TO_VALUE = {
        GameStatus.MARKER_MISS: -1,
        GameStatus.MARKER_HIT: 1,
        GameStatus.MARKER_EMPTY: 0
    }

    SHOT_REWARDS = {
        'invalid': -1,
        GameStatus.MARKER_HIT: 1,
        GameStatus.MARKER_MISS: 0
    }

    def __init__(self, render_mode=None):
        self.window_size = 660  # The size of the PyGame window

        self.observation_space = spaces.Box(
            low=-1,
            high=1,
            shape=(10, 10),
            dtype=np.int8
        )

        self.action_space = spaces.Discrete(100)

        self.player_game_status = None
        self.enemy_game_status = None
        self.enemy_player = None
        self.invalid_shots = 0
        self.shots = 0

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct frame rate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _get_obs(self):
        assert self.player_game_status is not None, "Call reset to get observations"

        obs = []
        for x in range(0, 10):
            row = []
            for y in range(0, 10):
                val = self.player_game_status.offence_board[y * 10 + x]
                row.append(BattleshipEnv.MARKER_TO_VALUE[val])
            obs.append(row)

        return np.array([np.array(xi, dtype=np.int8) for xi in obs])

    def _get_info(self):
        return {
            "invalid_shots": self.invalid_shots
        }

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # Reset game status
        self.player_game_status = GameStatus(10, 10)
        self.enemy_game_status = GameStatus(10, 10)
        self.enemy_player = RandomPlayer()
        self.enemy_player.update_game_status(self.enemy_game_status)
        self.enemy_game_status.set_defence_board(self.enemy_player.place_ships())
        self.invalid_shots = 0
        self.shots = 0

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        shot = self.player_game_status.__idx_to_shot__(action)

        # Update game status with the shot
        try:
            shot_result, ship_sunk, sunken_ship_type = self.enemy_game_status.add_defence_shot(shot)
            self.player_game_status.add_offence_shot(shot, shot_result, ship_sunk, sunken_ship_type)
        except InvalidShotException:
            shot_result = 'invalid'

        # An episode is done iff all the enemy ships sunk
        self.shots += 1
        if shot_result == 'invalid':
            self.invalid_shots += 1
        terminated = self.player_game_status.game_over
        truncated = not terminated and self.shots >= 100
        reward = BattleshipEnv.SHOT_REWARDS[shot_result]
        if terminated:
            reward += 1000
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_size, self.window_size)
            )
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        board_area = BoardArea(10, 10)
        board_area.update(self.player_game_status)

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(board_area.surface, (0, 0))
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(board_area.surface)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
