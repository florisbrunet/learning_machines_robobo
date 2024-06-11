import gym
from gym import spaces
import numpy as np
from robobo_interface import (
    IRobobo,
    SimulationRobobo,
    HardwareRobobo,
    Position,
    Orientation,
    WheelPosition
)

class RoboboEnv(gym.Env):
    def __init__(self, rob: IRobobo, target_position=None, max_steps=50):
        super(RoboboEnv, self).__init__()
        self.robot = rob
        self.target_position = target_position or np.array([1.0, 1.0])  # Default target position
        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)  # left speed, right speed, duration
        self.observation_space = spaces.Box(low=0, high=100, shape=(8,), dtype=np.float32)  # IR sensor readings
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self):
        self.robot.stop_simulation()  # Stop the simulation before resetting
        self.robot.play_simulation()  # Start the simulation again
        self.robot.set_position(Position(0, 0, 0), Orientation(0, 0, 0))
        self.robot.sleep(1)
        self.current_step = 0
        ir_data = np.array(self.robot.read_irs())
        return ir_data

    def step(self, action):
        self.current_step += 1

        # Ensure action values are within very conservative ranges
        left_speed = np.clip(action[0] * 10, -10, 10)  # [-10, 10]
        right_speed = np.clip(action[1] * 10, -10, 10)  # [-10, 10]
        duration = np.clip((action[2] + 1) / 2 * 25, 0, 25)  # [0, 25] milliseconds

        print(f"Action: left_speed={left_speed}, right_speed={right_speed}, duration={duration}")

        # Get current wheel positions to calculate speed changes
        current_wheel_position = self.robot.read_wheels()
        current_left_pos = current_wheel_position.wheel_pos_l
        current_right_pos = current_wheel_position.wheel_pos_r

        # Move the robot
        self.robot.move(left_speed, right_speed, int(duration))
        self.robot.sleep(duration / 1000.0)

        # Read new wheel positions to calculate actual speeds
        new_wheel_position = self.robot.read_wheels()
        new_left_pos = new_wheel_position.wheel_pos_l
        new_right_pos = new_wheel_position.wheel_pos_r

        # Calculate actual speeds (position change / duration)
        actual_left_speed = (new_left_pos - current_left_pos) / (duration / 1000.0)
        actual_right_speed = (new_right_pos - current_right_pos) / (duration / 1000.0)

        # Check if the robot tipped over
        orientation = self.robot.read_orientation()
        yaw, pitch, roll = orientation.yaw, orientation.pitch, orientation.roll
        tipping_threshold = 5  # Very conservative tipping threshold
        if abs(pitch) > tipping_threshold or abs(roll) > tipping_threshold:
            print("Tipping detected! Stopping movement.")
            self.robot.move(0, 0, 0)
            self.robot.sleep(1)  # Stop for a short duration to stabilize

        ir_data = np.array(self.robot.read_irs())
        reward = self.compute_reward(ir_data, actual_left_speed, actual_right_speed, pitch, roll)
        done = self.is_done(ir_data, pitch, roll)

        if self.current_step >= self.max_steps:
            done = True

        return ir_data, reward, done, {}

    def compute_reward(self, ir_data, left_speed, right_speed, pitch, roll):
        reward = 0

        # Collision Penalty
        if np.any(ir_data > 500):  # Collision threshold
            reward -= 50
            print("Collision detected!")

        # Progress Reward
        if left_speed != 0 or right_speed != 0:
            reward += 1  # Encourage movement
            print("Movement detected!")

        if left_speed == right_speed:
            reward += 1  # Discourage spinning in place
            print("Spinning in place detected!")

        # Idle Penalty
        min_movement_threshold = 1.0  # Define a minimum distance threshold
        if np.abs(left_speed) < min_movement_threshold and np.abs(right_speed) < min_movement_threshold:
            reward -= 1
            print("Idle detected!")

        # Proximity Penalty
        min_distance_to_obstacle = np.min(ir_data)
        if min_distance_to_obstacle > 0:  # Avoid division by zero
            reward -= 5 * (1 / min_distance_to_obstacle)
            print("Proximity detected!")

        # Tipping Penalty
        tipping_threshold = 5  # Very conservative tipping threshold
        if abs(pitch) > tipping_threshold or abs(roll) > tipping_threshold:
            reward -= 100  # Large penalty for tipping
            print("Tipping detected!")

        return reward

    def is_done(self, ir_data, pitch, roll):
        # Collision check
        if np.any(ir_data > 500):  # Collision threshold
            return True

        # Tipping check
        tipping_threshold = 5  # Very conservative tipping threshold
        if abs(pitch) > tipping_threshold or abs(roll) > tipping_threshold:
            return True

        return False

    def render(self, mode='human'):
        pass

    def close(self):
        self.robot.stop_simulation()
