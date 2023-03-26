import pexpect
import logging

# Config
ip_addr = "192.168.0.63"
user = "khalidowlwalid"
ssh_port = 22
# Set up the scp command with the appropriate arguments

# Define a logger object with the desired name
logger = logging.getLogger('my_logger')

# Set the logging level for the logger
logger.setLevel(logging.INFO)

# Create a console handler and set its logging level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it on the console handler
formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
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
    logging.info(child.before.decode())

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

