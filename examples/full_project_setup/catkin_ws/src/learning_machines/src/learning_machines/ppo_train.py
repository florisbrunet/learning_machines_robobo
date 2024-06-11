import gym
from stable_baselines3 import PPO
from .robobo_env import RoboboEnv
from robobo_interface import (
    IRobobo,
    Emotion,
    LedId,
    LedColor,
    SoundEmotion,
    SimulationRobobo,
    HardwareRobobo,
)   


def train_ppo_with_intervals(env, intervals, timesteps_per_interval):
    for i in range(intervals):
        model = PPO("MlpPolicy", env, verbose=1)
        model.learn(total_timesteps=timesteps_per_interval)
        model.save(f"ppo_robobo_interval_{i}")
        print(f"Interval {i} complete.")
        # Adjust reward logic if needed by modifying the environment
        # env.adjust_rewards(...)  # Placeholder for any reward adjustments

def run(rob: IRobobo):
    # Define the environment
    env = RoboboEnv(rob=rob)

    # Train the model with 10 intervals, each for 1000 timesteps
    train_ppo_with_intervals(env, intervals=2, timesteps_per_interval=100)

    env.close()
