import os
import can
import csv
import datetime
from scipy.io import savemat
import numpy as np


# TODO(Khalid): Create an arg parser, where user can give path on cli
# TODO(Khalid): Create a log file for this, so that it is easy to debug on different level
now = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
# TODO(Khalid): Create a config file for this?
# Config
id_of_interest = '0x11'
servo_saturation_value = 60
csv_path = f'datasets/datasets_{now}.csv'
mat_path = f'datasets/datasets_{now}.mat'

# Setup can0 channel
os.system('sudo ip link set can0 up type can bitrate 125000')
os.system('sudo ifconfig can0 up') # Enable can0 

bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native

keyboard_interrupt_flag = False

datasets = []
throttle_datasets = []
servo_setpoint_datasets = []

while not keyboard_interrupt_flag:
    try:
        message = bus.recv(10.0)
        
        # This returns the int value of the id
        message_id = message.arbitration_id

        # Cast it into hexadecimal format
        message_id_hex = str(hex(int(message_id)))
         
        if message_id_hex != id_of_interest:
            print("Ignoring")
            continue

        else:
                
            # Extract the data from the message
            data = message.data.hex()

            # TODO(Khalid): Create a function for this (clean up code)
            # TODO (Khalid): Make sure that we also check the id
            # Separate it into 16 bits
            # Data is in little-endian format 
            throttle_percentage_LE = data[4:7+1]
            servo_setpoint_LE = data[8:11+1]

            # Python int cast expects big endian, so we need to convert data from
            # Little Endian to Big Endian
            throttle_percentage_LSB = throttle_percentage_LE[0:2]
            throttle_percentage_MSB = throttle_percentage_LE[2:]

            servo_setpoint_LSB = servo_setpoint_LE[0:2]
            servo_setpoint_MSB = servo_setpoint_LE[2:]
            
            # Concatenate the string to format into Big Endian
            throttle_percentage_BE = throttle_percentage_MSB + throttle_percentage_LSB
            servo_setpoint_BE = servo_setpoint_MSB + servo_setpoint_LSB
            
            # Cast it into int value
            throttle_percentage_int = int(throttle_percentage_BE, 16)
            servo_setpoint_int = int(servo_setpoint_BE, 16)

            # Scale it accordingly
            throttle_percentage = throttle_percentage_int / 100
            servo_setpoint = servo_setpoint_int / 100

            print(f"Servo Setpoint: {servo_setpoint} | Throttle_percentage: {throttle_percentage}")

            datasets.append((servo_setpoint, throttle_percentage))
            throttle_datasets.append(throttle_percentage)
            servo_setpoint_datasets.append(servo_setpoint)

            if servo_setpoint > servo_saturation_value:
                print("Servo saturation value reaced, Initialised Shutdown")
                raise KeyboardInterrupt

            if message is None:
                print('Timeout occurred, no message received.')
        
    # If user interrupts using keyboard, shutdown or it needs to be if it reaches the saturation
    # value of the servo setpoint
    except KeyboardInterrupt:
        print("Keyboard Interrupt. Initialise shutdown")
        keyboard_interrupt_flag = True

print("Shutting down can0 socket")
os.system('sudo ifconfig can0 down')

# Check if datasets are of the same length
# This is to ensure that each datasets has its pair
assert len(servo_setpoint_datasets) == len(throttle_datasets), f"Servo Setpoints ({servo_setpoint_datasets}) and Throttle datasets ({throttle_datasets}) is not of the same length"

servo_setpoint_datasets = np.array(list(map(float, servo_setpoint_datasets)))
throttle_datasets = np.array(list(map(float, throttle_datasets)))

step = 0.01
interpolated_throttle_feedback = np.arange(0, 100 + step, step, dtype='float')
interpolated_servo_setpoint = np.interp(interpolated_throttle_feedback, throttle_datasets, servo_setpoint_datasets)

interpolated_datasets =  np.column_stack((interpolated_throttle_feedback, interpolated_servo_setpoint))

print("Writing data into csv file...")
# Store populated datasets into csv file
np.savetxt(csv_path, interpolated_datasets, delimiter=',')
print("Datasets saved in .csv format at {csv_path}")

print("Writing into .mat file...")
savemat(mat_path, {'datasets': interpolated_datasets}, appendmat=False)
print("Datasets saved in .mat format at {mat_path}")
