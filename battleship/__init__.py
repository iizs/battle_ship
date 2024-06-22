from gymnasium.envs.registration import register
from battleship.gym_env import GridWorldEnv

register(
     id="battleship/GridWorld-v0",
     entry_point="battleship:GridWorldEnv",
     max_episode_steps=300,
)

