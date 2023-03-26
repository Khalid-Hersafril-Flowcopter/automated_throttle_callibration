import pexpect

# Config
ip_addr = "192.168.0.63"
user = "khalidowlwalid"
ssh_port = 22
# Set up the scp command with the appropriate arguments

scp_command = f"scp test.txt {user}@{ip_addr}:~/Downloads/"

try:
    # Start the scp command using pexpect
    child = pexpect.spawn(scp_command)

    # Wait for the password prompt
    child.expect("password:")

    # Enter the password
    child.sendline("your_password")

    # Wait for the transfer to complete
    child.expect(pexpect.EOF)

    # Print the output
    print(child.before)

except pexpect.exceptions.TIMEOUT:
    print("Connection timed out")

except pexpect.exceptions.EOF:
    args = child.args
    before = str(child.before)
    print(before)

    if "connection refused" in before.lower():
        print(f"Connect to host {ip_addr} at port {ssh_port}: Connection refused. Please check if you have enabled your port is enabled.")
    print("SCP command exited unexpectedly")

except pexpect.exceptions.ExceptionPexpect as e:
    print(f"An exception occurred: {str(e)}")

