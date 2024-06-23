from gymnasium.envs.registration import register
from battleship.gym_env import BattleshipEnv

register(
     id="battleship/BattleshipEnv-v0",
     entry_point="battleship:BattleshipEnv",
     max_episode_steps=300,
)

