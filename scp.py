import pexpect
import logging

# Config
ip_addr = "192.168.0.63"
user = "khalidowlwalid"
ssh_port = 22
logger_name = 'throttle_callibrator'

# Set up the scp command with the appropriate arguments

# Create a logger object with the desired name
logger = logging.getLogger(logger_name)

logging.getLogger().setLevel(logging.NOTSET)

# Create a file handler and set its logging level
file_handler = logging.FileHandler('my_log_file.log')

# Create a formatter and set it on the file handler
formatter = logging.Formatter(f'{logger.name}: %(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.NOTSET)
console_handler.setFormatter(formatter)

# Add the file handler to the logger object
logger.addHandler(file_handler)
logger.addHandler(console_handler)

scp_command = f"scp -P {ssh_port} test.txt {user}@{ip_addr}:~/Downloads/"

try:
    # Start the scp command using pexpect
    child = pexpect.spawn(scp_command)

    # Wait for the password prompt
    child.expect("password:")

    # Enter the password
    child.sendline("jellybean123")

    # Wait for the transfer to complete
    child.expect(pexpect.EOF)

    # Useful for debugging
    logger.info("Hello")
    logger.info(child.before.decode())
    logger.error("Error")
    logger.warning("test")
    logger.debug("debug")

    file_transfer_flag = "100%" in child.before.decode()

    if file_transfer_flag:
        logger.info("Successfully transferred file..")
    else:
        logger.info("File not transferred")

except pexpect.exceptions.TIMEOUT:
    logger.error("Connection timed out")
    logger.error("Check if your password has been correctly set")

except pexpect.exceptions.EOF:
    args = child.args
    before = str(child.before)
    logger.error(before)

    if "connection refused" in before.lower():
        logger.error(f"Connect to host {ip_addr} at port {ssh_port}: Connection refused. Please check if you have enabled your port is enabled.")
    logger.error("SCP command exited unexpectedly")

except pexpect.exceptions.ExceptionPexpect as e:
    logger.error(f"An exception occurred: {str(e)}")

