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

# Config for scp
ip_addr = "192.168.0.63"
user = "khalidowlwalid"
ssh_port = 22
logger_name = 'throttle_callibrator'
saved_file_path = '~/Documents/'

# Setup the logger for the session
logger = logging.getLogger(logger_name)
logging.getLogger().setLevel(logging.NOTSET)

# Create a file handler and set its logging level
file_handler = logging.FileHandler('log/automated_throttle_callibration.log')

# Create a formatter and set it on the file handler
formatter = logging.Formatter(f'{logger.name}: [%(asctime)s][%(levelname)s]: %(message)s')
file_handler.setFormatter(formatter)

# Show logging in terminal/console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.NOTSET)
console_handler.setFormatter(formatter)

# Add the file handler to the logger object
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
            logger.info("Ignoring")
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

            logger.info(f"Servo Setpoint: {servo_setpoint} | Throttle_percentage: {throttle_percentage}")

            datasets.append((servo_setpoint, throttle_percentage))
            throttle_datasets.append(throttle_percentage)
            servo_setpoint_datasets.append(servo_setpoint)

            if servo_setpoint > servo_saturation_value:
                logger.info("Servo saturation value reaced, Initialised Shutdown")
                raise KeyboardInterrupt

            if message is None:
                logger.info('Timeout occurred, no message received.')

    # If user interrupts using keyboard, shutdown or it needs to be if it reaches the saturation
    # value of the servo setpoint
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt. Initialise shutdown")
        keyboard_interrupt_flag = True

logger.info("Shutting down can0 socket")
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

logger.info("Writing data into csv file...")
# Store populated datasets into csv file
np.savetxt(csv_path, interpolated_datasets, delimiter=',')
logger.info("Datasets saved in .csv format at {csv_path}")

logger.info("Writing into .mat file...")
savemat(mat_path, {'datasets': interpolated_datasets}, appendmat=False)
logger.info("Datasets saved in .mat format at {mat_path}")

# Start the scp command using pexpect
scp_command = f"scp -P {ssh_port} {mat_path} {user}@{ip_addr}:{saved_file_path}"
child = pexpect.spawn(scp_command)

login_success_flag = False

failed_attempts = 0

while not login_success_flag:
    try:

        # Wait for the password prompt
        child.expect("password:")

        # Enter password
        user_password = getpass.getpass(f"{user}@{ip_addr}'s password:")
        child.sendline(user_password)

        index_flag = child.expect([mat_path, "Permission denied", "password:"])

        if index_flag == 0:
            logger.info("Login successful!")
            login_success_flag = True
        elif index_flag == 1 or index_flag == 2:
            logger.error("Permission denied. Wrong password. Please try again")
            failed_attempts += 1

            if failed_attempts == 3:
                logger.error(f"Maximum number of attempts reached. File will not be saved to {user}@{ip_addr}'s {saved_file_path}")
                logger.info(f"User will need to download the file locally from the Raspberry Pi. The full path of the file can be found in {mat_path}.")
                raise KeyboardInterrupt

            continue

        """
        -----------------------------------------------
        Example prompt response during successful login
        -----------------------------------------------
        Password:
        sending incremental file list
        example.txt
              7 100%    0.00kB/s    0:00:00 (xfer#1, to-check=0/1)

        sent 28 bytes  received 33 bytes  122.00 bytes/sec
        total size is 7  speedup is 0.08

        EOF
        """

        # Wait for the transfer to complete
        child.expect(pexpect.EOF)

        # Useful for debugging
        logger.info(f"Output: {child.before.decode()}")

        # Check if file is completely transferred or not
        file_transfer_flag = "100%" in child.before.decode()

        if file_transfer_flag:
            logger.info("Successfully transferred file..")
            logger.info(f"File saved in {saved_file_path}")
        else:
            logger.warning("File not transferred")

    # Check for timeout
    except pexpect.exceptions.TIMEOUT:
        logger.error("Connection timed out")
        logger.error("Check if your password has been correctly set")

    # Check if for any reason, something breaks the command
    except pexpect.exceptions.EOF:
        before = str(child.before)
        logger.info(child)

        if "connection refused" in before.lower():
            logger.error(f"Connect to host {ip_addr} at port {ssh_port}: Connection refused. Please check if you have enabled your port is enabled.")
        logger.error("SCP command exited unexpectedly")

    except pexpect.exceptions.ExceptionPexpect as e:
        logger.error(f"An exception occurred: {str(e)}")

    # Allow user to exit with keyboard
    except KeyboardInterrupt:
        login_success_flag = True
        logger.info("Keyboard Interrupt. Shutting down..")
