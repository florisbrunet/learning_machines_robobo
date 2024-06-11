import cv2
import matplotlib.pyplot as plt
import csv
from data_files import FIGRURES_DIR
from robobo_interface import IRobobo, SimulationRobobo, HardwareRobobo
import os
from datetime import datetime


current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")

simulation = True
multiple_runs = False
count_runs = 5

type_arena = "similar_to_irl_gp"

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


SENSOR_DODGE_THRESHOLDS = {
    'FrontC': 11,
    'FrontRR': 15,
    'FrontLL': 15,
    'FrontL': 80,
    'FrontR': 80,
}

BIG_DODGE_THRESHOLDS = {
    'FrontC': 90,
    'FrontRR': 90,
    'FrontLL': 90,
}

WHEEL_SPEED = 50
MOVE_BACK = -WHEEL_SPEED, -WHEEL_SPEED, 900
TURN_RIGHT = 25, -25, 650
TURN_LEFT = -25, 25, 650
MOVE_FORWARD = WHEEL_SPEED, WHEEL_SPEED, 350
MOVE_FAST = 75, 75, 350

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

def sens_test(rob: IRobobo, steps: int = 100):
    """Task: Never collide with obstacles or walls. If an obstacle is detected, dodge it. If a wall is detected, dodge it."""
    sensor_readings = []
    
    total_steps = 0
    irs_logs = []
    if simulation:
        rob.play_simulation()
        # time.sleep(5)  # Ensure the simulation is properly initialized
    rob.sleep(1)

    try:
        for step in range(steps):
            print(f"Step: {step}")
            total_steps += 1
            
            try:
                irs = rob.read_irs()
                print(f"\n 'FrontC': {irs[4]}\n 'FrontLL': {irs[7]}\n 'FrontRR': {irs[5]}\n 'FrontL(45)': {irs[2]}\n 'FrontR(45)': {irs[3]}\n 'BackC': {irs[6]}\n 'BackL': {irs[0]}\n 'BackR': {irs[1]}'\n\n")
                
            except Exception as e:
                print(f"Error reading IR sensors: {e}")
                break
            rob.move(MOVE_FORWARD)

            

            sensor_readings.append(irs)
    finally:
        if simulation:
            rob.stop_simulation()
        print("Done")
        print(f"Steps episode: {total_steps}")

    metadata = {
        
        'total_steps': total_steps,
        'irs_logs': irs_logs,
        'sensor_thresholds': SENSOR_THRESHOLDS,
        'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
        'wall_dodge_thresholds': BIG_DODGE_THRESHOLDS,
    }

    return sensor_readings, metadata

def run_all_actions(rob: IRobobo):
    if multiple_runs:
        for i in range(count_runs):
            grouped_data_dir = create_output_dirs(simulation, i)
            meta_data = {
                'date_time': current_datetime,
                'simulation': simulation,
                'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
                'wall_dodge_thresholds': BIG_DODGE_THRESHOLDS
            }
            if isinstance(rob, SimulationRobobo) and simulation:
                rob.play_simulation()

            sensor_readings, task_metadata = task0_group_6(rob, steps=100)
            meta_data.update(task_metadata)
            save_meta_data(meta_data, 'meta_data_final.txt', grouped_data_dir)
            save_to_csv(sensor_readings, str(grouped_data_dir / f"data_{current_datetime}.csv"))
            plot_sensor_data(sensor_readings, 'Task0 Group6', grouped_data_dir)

            if isinstance(rob, SimulationRobobo) and simulation:
                rob.stop_simulation()
    else:
        grouped_data_dir = create_output_dirs(simulation, None)
        meta_data = {
            'date_time': current_datetime,
            'simulation': simulation,
            'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
            'wall_dodge_thresholds': BIG_DODGE_THRESHOLDS
        }
        if isinstance(rob, SimulationRobobo) and simulation:
            rob.play_simulation()

        sensor_readings, task_metadata = task0_group_6(rob, steps=100)
        meta_data.update(task_metadata)
        save_meta_data(meta_data, 'meta_data_final.txt', grouped_data_dir)
        save_to_csv(sensor_readings, str(grouped_data_dir / f"data_{current_datetime}.csv"))
        plot_sensor_data(sensor_readings, 'Task0 Group6', grouped_data_dir)

        if isinstance(rob, SimulationRobobo) and simulation:
            rob.stop_simulation()