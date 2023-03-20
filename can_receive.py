import os
import can

os.system('sudo ip link set can0 up type can bitrate 125000')
os.system('sudo ifconfig can0 up') # Enable can0 

bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native

keyboard_interrupt_flag = False

while not keyboard_interrupt_flag:
    try:
        message = bus.recv(10.0)
        
        # TODO(Khalid): Create a config file for this?
        id_of_interest = '0x11'
        
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
            if message is None:
                print('Timeout occurred, no message received.')
        
    # If user interrupts using keyboard, shutdown or it needs to be if it reaches the saturation
    # value of the servo setpoint
    except KeyboardInterrupt:
        print("Keyboard Interrupt. Initialise shutdown")
        keyboard_interrupt_flag = True

print("Shutting down can0 socket")
os.system('sudo ifconfig can0 down')
