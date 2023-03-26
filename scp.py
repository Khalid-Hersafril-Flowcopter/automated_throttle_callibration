import pexpect
import logging
import time

# Config
ip_addr = "192.168.0.63"
user = "khalidowlwalid"
ssh_port = 22
logger_name = 'throttle_callibrator'
user_password = 'jellybean123'
user_path = '~/Documents/'
file_name = 'test.txt'

# Set up the scp command with the appropriate arguments

# Create a logger object with the desired name
logger = logging.getLogger(logger_name)

logging.getLogger().setLevel(logging.NOTSET)

# Create a file handler and set its logging level
file_handler = logging.FileHandler('my_log_file.log')

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

scp_command = f"scp -P {ssh_port} {file_name} {user}@{ip_addr}:{user_path}"

try:
    # Start the scp command using pexpect
    child = pexpect.spawn(scp_command)

    # Wait for the password prompt
    child.expect("password:")

    # Enter password
    child.sendline(user_password)


    index_flag = child.expect([file_name, "Permission denied", "password:"])

    if index_flag == 0:
        logger.info("Login successful!")

    elif index_flag == 1 or index_flag == 2:
        logger.error("Permission denied. Wrong password. Please try again")
        raise KeyboardInterrupt

    # Check if user inputs wrong password
    # If not, then child expects to see the shell prompt, hence the $
    # index_flag = child.expect(["Permission denied", "password:"], timeout=5)

#    if index_flag == 0:
#        logger.info("Permission denied. Check your password and try again")

        # Raise keyboard interrupt to avoid waiting time
#        raise KeyboardInterrupt
#    elif index_flag == 1:
#        logger.info("Login successful!")
#    else:
#        logger.info("Timeout reached: Login unsuccesful.")
#        raise pexpect.exceptions.TIMEOUT

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
        logger.info(f"File saved in {user_path}")
    else:
        logger.warning("File not transferred")

# Check for timeout
except pexpect.exceptions.TIMEOUT:
    logger.error("Connection timed out")
    logger.error("Check if your password has been correctly set")

# Check if for any reason, something breaks the command
except pexpect.exceptions.EOF:
    before = str(child.before)
    print(child)

    if "connection refused" in before.lower():
        logger.error(f"Connect to host {ip_addr} at port {ssh_port}: Connection refused. Please check if you have enabled your port is enabled.")
    logger.error("SCP command exited unexpectedly")

except pexpect.exceptions.ExceptionPexpect as e:
    logger.error(f"An exception occurred: {str(e)}")

# Allow user to exit with keyboard
except KeyboardInterrupt:
    logger.info("Keyboard Interrupt. Shutting down..")
