import cv2
import matplotlib.pyplot as plt
import csv
from data_files import FIGRURES_DIR
from robobo_interface import IRobobo, SimulationRobobo, HardwareRobobo
import os
from datetime import datetime

current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S") 

simulation = True
multiple_runs = True
count_runs = 10

type_arena = "similar_to_irl"



# Sensor thresholds (all)
SENSOR_THRESHOLDS = {
    'BackL': 10,
    'BackR': 10,
    'FrontL': 10,
    'FrontR': 10,
    'FrontC': 10,
    'FrontRR': 10,
    'BackC': 60,
    'FrontLL': 10,
}

if simulation:
    # Thresholds specific to simulation
    SENSOR_DODGE_THRESHOLDS = {
        'FrontC': 25,
        'FrontRR': 50,
        'FrontLL': 50,
        'FrontL': 380,
        'FrontR': 380,
    }

    WALL_DODGE_THRESHOLDS = {
        'FrontC': 250,
        'FrontRR': 250,
        'FrontLL': 250,
    }
    
    WHEEL_SPEED = 77
    MOVE_BACK = -WHEEL_SPEED, -WHEEL_SPEED, 2500
    TURN_RIGHT = WHEEL_SPEED, -WHEEL_SPEED, 500
    TURN_LEFT = -WHEEL_SPEED, WHEEL_SPEED, 500
    MOVE_FORWARD = WHEEL_SPEED, WHEEL_SPEED, 300
else:
    # Thresholds specific to hardware
    SENSOR_DODGE_THRESHOLDS = {
        'FrontC': 30,
        'FrontRR': 20,
        'FrontLL': 20,
        'FrontL': 80,
        'FrontR': 80,
    }

    WALL_DODGE_THRESHOLDS = {
        'FrontC': 80,
        'FrontRR': 80,
        'FrontLL': 80,
    }
    
    WHEEL_SPEED = 50
    MOVE_BACK = -WHEEL_SPEED, -WHEEL_SPEED, 1000
    TURN_RIGHT = WHEEL_SPEED, -WHEEL_SPEED, 850
    TURN_LEFT = -WHEEL_SPEED, WHEEL_SPEED, 850
    MOVE_FORWARD = WHEEL_SPEED, WHEEL_SPEED, 350

def create_output_dirs(simulation, run):
    sim_or_hard = "_sim" if simulation else "_hard"
    if multiple_runs:
        grouped_data_dir = FIGRURES_DIR / "grouped_data" / f"runs{count_runs}_{current_datetime}" / f"{current_datetime}{sim_or_hard}_{type_arena}_run{run}"
    else:
        grouped_data_dir = FIGRURES_DIR / "grouped_data" / f"{current_datetime}{sim_or_hard}_{type_arena}"

    os.makedirs(grouped_data_dir, exist_ok=True)
    return grouped_data_dir

def plot_sensor_data(irs, title, grouped_data_dir):
    plt.figure()
    for sensor_index in range(len(irs[0])):
        sensor_values = [data[sensor_index] for data in irs]
        plt.plot(sensor_values, label=f'Sensor {sensor_index + 1}')
    plt.xlabel('Steps')
    plt.ylabel('IR Sensor Values')
    plt.title(title)
    plt.legend()
    plt.savefig(str(grouped_data_dir / f"{title}_sensor_plot_{current_datetime}.png"))

def save_to_csv(sensor_readings, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR', 'BackC', 'FrontLL', 'WallDodge', 'ObstacleDodge'])
        for data in sensor_readings:
            writer.writerow(data)

def save_meta_data(metadata, filename, grouped_data_dir):
    with open(grouped_data_dir / filename, 'w') as file:
        for key, value in metadata.items():
            file.write(f"{key}: {value}\n")

def task0_group_6(rob: IRobobo, steps: int = 100):
    """Task: Never collide with obstacles or walls. If an obstacle is detected, dodge it. If a wall is detected, dodge it."""
    sensor_readings = []
    obstacle_dodges = 0
    wall_dodges = 0
    consecutive_obstacle_dodges = 0
    consecutive_wall_dodges = 0
    total_steps = 0
    irs_logs = []
    if simulation:
        rob.play_simulation()
    try:
        for step in range(steps):
            print(f"Step: {step}")
            total_steps += 1
            irs = rob.read_irs()
            is_obstacle_dodge = 0
            is_wall_dodge = 0
            if consecutive_obstacle_dodges >= 3:
                print("Too many consecutive obstacle dodges")
                if irs[6] > SENSOR_THRESHOLDS['BackC']:
                    rob.move(-50, -50, 1000)
                    rob.sleep(1)
                else:
                    rob.move(*MOVE_BACK)  # Move backward
                    rob.sleep(2.5)
            if consecutive_wall_dodges >= 3:
                print("Too many consecutive wall dodges")
                rob.move(0,0,0)
                rob.sleep(1)
                rob.move(-100, -100, 5000)
                  
            

            # Wall dodge condition
            if any(irs[i] > WALL_DODGE_THRESHOLDS[key] for i, key in zip([4, 5, 7], ['FrontC', 'FrontRR', 'FrontLL'])):
                print(f"\n\n 'FrontC': {irs[4]}\n 'FrontLL': {irs[7]}\n 'FrontRR': {irs[5]}\n 'FrontL(45)': {irs[2]}\n 'FrontR(45)': {irs[3]}\n 'BackC': {irs[6]}\n 'BackL': {irs[0]}\n 'BackR': {irs[1]}'\n\n")
                irs_logs.append({'step': step, 'type': 'wall_dodge', 'values': irs})
                rob.move(*MOVE_BACK)  # Move backward
                rob.sleep(2.5)
                rob.move(0, 0, 0)  # Stop
                if irs[5] > WALL_DODGE_THRESHOLDS['FrontRR']:
                    rob.move(*TURN_LEFT)  # Turn right 90 degrees
                elif irs[7] > WALL_DODGE_THRESHOLDS['FrontLL']:
                    rob.move(*TURN_RIGHT)  # Turn left 90 degrees
                else:
                    rob.move(*TURN_RIGHT)  # Turn right 90 degrees
                rob.sleep(0.85)
                print("-------------Wall Dodge----------------")
                wall_dodges += 1
                is_wall_dodge = 1
                consecutive_obstacle_dodges = 0
                consecutive_wall_dodges += 1
                print(f"Steps run: {step + 1} for wall_dodge: {wall_dodges}")
            
            # Obstacle dodge condition
            elif any(irs[i] > SENSOR_DODGE_THRESHOLDS[key] for i, key in zip([4, 5, 7, 2, 3], ['FrontC', 'FrontRR', 'FrontLL', 'FrontL', 'FrontR'])):
                print(f"\n\n 'FrontC': {irs[4]}\n 'FrontLL': {irs[7]}\n 'FrontRR': {irs[5]}\n 'FrontL(45)': {irs[2]}\n 'FrontR(45)': {irs[3]}\n 'BackC': {irs[6]}\n 'BackL': {irs[0]}\n 'BackR': {irs[1]}'\n\n")
                irs_logs.append({'step': step, 'type': 'obstacle_dodge', 'values': irs})
                rob.move(0, 0, 0)  # Stop
                rob.sleep(0.1)
                if irs[5] > SENSOR_DODGE_THRESHOLDS['FrontRR']:
                    rob.move(*TURN_LEFT)  # Turn right 90 degrees
                elif irs[7] > SENSOR_DODGE_THRESHOLDS['FrontLL']:
                    rob.move(*TURN_RIGHT)  # Turn left 90 degrees
                else:
                    rob.move(*TURN_RIGHT)  # Turn right 90 degrees
                rob.sleep(0.85)
                print("Obstacle Dodge")
                obstacle_dodges += 1
                is_obstacle_dodge = 1
                consecutive_obstacle_dodges += 1
                consecutive_wall_dodges = 0

            # Move forward
            else:
                consecutive_obstacle_dodges = 0
                consecutive_wall_dodges = 0
                if irs[4] < 5.82: # median = 5.845700385106792:
                    print("Clear space ahead")
                    rob.move(150, 150, 1000)
                    rob.sleep(0.5)
                else:
                    rob.move(*MOVE_FORWARD)
                    rob.sleep(0.11)

            # if wall_dodges == 4:
            #     break

            sensor_readings.append(irs + [is_wall_dodge, is_obstacle_dodge])
    finally:
        if simulation:
            rob.stop_simulation()
        print("Done")
        print(f"Steps episode: {total_steps}")
    
    metadata = {
        'obstacle_dodges': obstacle_dodges,
        'wall_dodges': wall_dodges,
        'total_steps': total_steps,
        'irs_logs': irs_logs,
        'sensor_thresholds': SENSOR_THRESHOLDS,
        'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
        'wall_dodge_thresholds': WALL_DODGE_THRESHOLDS,
    }

    return sensor_readings, metadata

def run_all_actions(rob: IRobobo):
    if multiple_runs:
        for i in range(count_runs):
            current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S") 
            grouped_data_dir = create_output_dirs(simulation, i)
            meta_data = {
                'date_time': current_datetime,
                'simulation': simulation,
                'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
                'wall_dodge_thresholds': WALL_DODGE_THRESHOLDS
            }
            if isinstance(rob, SimulationRobobo) and simulation:
                rob.play_simulation()
            
            sensor_readings, task_metadata = task0_group_6(rob, steps=250)
            meta_data.update(task_metadata)
            save_meta_data(meta_data, 'meta_data_final.txt', grouped_data_dir)
            save_to_csv(sensor_readings, str(grouped_data_dir / f"data_{current_datetime}.csv"))
            plot_sensor_data(sensor_readings, 'Task0 Group6', grouped_data_dir)
            
            if isinstance(rob, SimulationRobobo) and simulation:
                rob.stop_simulation()
    else:
        grouped_data_dir = create_output_dirs(simulation)
        meta_data = {
            'date_time': current_datetime,
            'simulation': simulation,
            'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
            'wall_dodge_thresholds': WALL_DODGE_THRESHOLDS
        }
        if isinstance(rob, SimulationRobobo) and simulation:
            rob.play_simulation()
        
        sensor_readings, task_metadata = task0_group_6(rob, steps=250)
        meta_data.update(task_metadata)
        save_meta_data(meta_data, 'meta_data_final.txt', grouped_data_dir)
        save_to_csv(sensor_readings, str(grouped_data_dir / f"data_{current_datetime}.csv"))
        plot_sensor_data(sensor_readings, 'Task0 Group6', grouped_data_dir)
        
        if isinstance(rob, SimulationRobobo) and simulation:
            rob.stop_simulation()
