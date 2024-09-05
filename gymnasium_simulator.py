import battleship
import gymnasium as gym
from collections import defaultdict
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

env = gym.make('battleship/BattleshipEnv-v0', render_mode="rgb_array")


class Agent:
    @staticmethod
    def __observation_to_str__(obs):
        s = ''
        for row in obs:
            s += ''.join([str(e) for e in row])
        return s

    def __init__(
        self,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        # TODO implement more properly
        # with probability epsilon return a random action to explore the environment
        if np.random.random() < self.epsilon:
            # random except minus reward
            return np.random.choice(np.flatnonzero(self.q_values[Agent.__observation_to_str__(obs)] >= 0))

        # with probability (1 - epsilon) act greedily (exploit)
        else:
            return np.random.choice(np.flatnonzero(self.q_values[Agent.__observation_to_str__(obs)] == self.q_values[Agent.__observation_to_str__(obs)].max()))
            # return int(np.argmax(self.q_values[Agent.__observation_to_str__(obs)]))

    def update(
        self,
        obs,
        action: int,
        reward: float,
        terminated: bool,
        next_obs,
    ):
        """Updates the Q-value of an action."""
        # TODO implement more properly
        future_q_value = np.max(self.q_values[Agent.__observation_to_str__(next_obs)])
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[Agent.__observation_to_str__(obs)][action]
        )

        self.q_values[Agent.__observation_to_str__(obs)][action] = (
            self.q_values[Agent.__observation_to_str__(obs)][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)

# hyperparameters
learning_rate = 1  # 0.01
n_episodes = 10_000  # 100_000
start_epsilon = 1.0
epsilon_decay = start_epsilon / (n_episodes / 2)  # reduce the exploration over time
final_epsilon = 0.1

agent = Agent(
    learning_rate=learning_rate,
    initial_epsilon=start_epsilon,
    epsilon_decay=epsilon_decay,
    final_epsilon=final_epsilon,
)

env = gym.wrappers.RecordEpisodeStatistics(env, deque_size=n_episodes)
for episode in tqdm(range(n_episodes)):
    obs, info = env.reset()
    done = False

    # play one episode
    while not done:
        action = agent.get_action(obs)
        next_obs, reward, terminated, truncated, info = env.step(action)

        # update the agent
        agent.update(obs, action, reward, terminated, next_obs)

        # update if the environment is done and the current obs
        done = terminated or truncated
        obs = next_obs

    agent.decay_epsilon()


rolling_length = 100 # 500
fig, axs = plt.subplots(ncols=3, figsize=(12, 5))
axs[0].set_title("Episode rewards")
# compute and assign a rolling average of the data to provide a smoother graph
reward_moving_average = (
    np.convolve(
        np.array(env.return_queue).flatten(), np.ones(rolling_length), mode="valid"
    )
    / rolling_length
)
axs[0].plot(range(len(reward_moving_average)), reward_moving_average)
axs[1].set_title("Episode lengths")
length_moving_average = (
    np.convolve(
        np.array(env.length_queue).flatten(), np.ones(rolling_length), mode="same"
    )
    / rolling_length
)
axs[1].plot(range(len(length_moving_average)), length_moving_average)
axs[2].set_title("Training Error")
training_error_moving_average = (
    np.convolve(np.array(agent.training_error), np.ones(rolling_length), mode="same")
    / rolling_length
)
axs[2].plot(range(len(training_error_moving_average)), training_error_moving_average)
plt.tight_layout()
plt.show()
