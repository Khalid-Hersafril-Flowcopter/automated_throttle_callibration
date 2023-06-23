import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy

import signal

def signal_handler(signal, frame):
    print("Force closing the application...")
    # Perform any necessary cleanup or termination steps here
    # ...

# Register the signal handler function
signal.signal(signal.SIGINT, signal_handler)

path_to_excel = "/home/khalidowlwalid/Documents/Flowcopter/automated_throttle_callibration/tests/servoToECU.xlsx"
path_to_mat = "/home/khalidowlwalid/Documents/Flowcopter/automated_throttle_callibration/tests/ecuToServ.mat"
dataFrame = pd.read_excel(path_to_excel, sheet_name="Sheet1")
commandedServo = dataFrame.iloc[:,0].values
throttleFeedback = dataFrame.iloc[:,2].values

step = 0.01
interpolated_throttle_feedback = np.arange(0, 100 + step, step, dtype='float')
interpolated_servo_setpoint = np.interp(interpolated_throttle_feedback, throttleFeedback, commandedServo)

interpolated_datasets =  np.column_stack((interpolated_throttle_feedback, interpolated_servo_setpoint))

benchmarkData = scipy.io.loadmat(path_to_mat)

benchmarkThrottleFeedback = benchmarkData['ecuToServ'][:,0]
benchmarkServoSetpoint = benchmarkData['ecuToServ'][:,1]

try:
    fig, ax = plt.subplots()
    ax.plot(interpolated_datasets[:,1], interpolated_datasets[:,0])
    ax.plot(benchmarkServoSetpoint, benchmarkThrottleFeedback)
    plt.show()
except KeyboardInterrupt:
    print("Shutting down")