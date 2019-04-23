#!/usr/bin/env python3
''' Demo how your robot can follow an object with Pixy for LEGO Mindstorms.

    NOTE: this demo ifs for the first version of Pixy2 for LEGO Mindstorms.
          Use pixy2_chaser.py for the new Pixy2 for LEGO Mindstorms.

    Requirements:
        Hardware: - LEGO EV3-brick.
                  - Pixy for LEGO Mindstorms, attached to input port 1.
                    Set Pixy to detect signature 1 (see documentation Pixy).
                  - LEGO TouchSensor, attached to input port 4.
                  - Two LEGO LargeMotors, attached to output ports A and B.
        Software: - ev3dev operating system.

    Kees Smit, 2019
    github:  github.com/KWSmit
    website: kwsmit.github.io
'''

from ev3dev2.sensor import Sensor, INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from ev3dev2.port import LegoPort
from time import sleep


def limit_speed(speed):
    """ Limit speed in range [-1000,1000] """
    if speed > 1000:
        speed = 1000
    elif speed < -1000:
        speed = -1000
    return speed

# Set LEGO port for Pixy on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'auto'
sleep(2)

# Connect Pixy camera
pixy = Sensor(INPUT_1)
# Set mode to detect signature 1 only
pixy.mode = 'SIG1'

# Signatures we're interested in (SIG1)
sig = 1

# Connect TouchSensor (to stop script)
ts = TouchSensor(INPUT_4)

# Connect LargeMotors
rmotor = LargeMotor(OUTPUT_A)
lmotor = LargeMotor(OUTPUT_B)

# Defining constants
X_REF = 128  # X-coordinate of referencepoint
Y_REF = 150  # Y-coordinate of referencepoint
KP = 0.4     # Proportional constant PID-controller
KI = 0.01    # Integral constant PID-controller
KD = 0.05    # Derivative constant PID-controller
GAIN = 10    # Gain for motorspeed

# Initializing PID variables
integral_x = 0
derivative_x = 0
last_dx = 0
integral_y = 0
derivative_y = 0
last_dy = 0

# Data for requesting block
data = [174, 193, 32, 2, sig, 1]

while not ts.value():
    if pixy.value(0) > 0:
        # SIG1 detected, control motors
        x = pixy.value(1)               # X-centroid of largest SIG1-object
        y = pixy.value(2)               # Y-centroid of largest SIG1-object
        dx = X_REF - x                  # Error in reference to X_REF
        integral_x = integral_x + dx    # Calculate integral for PID
        derivative_x = dx - last_dx     # Calculate derivative for PID
        speed_x = KP*dx + KI*integral_x + KD*derivative_x  # Speed X-direction
        dy = Y_REF - y                  # Error in reference to Y_REF
        integral_y = integral_y + dy    # Calculate integral for PID
        derivative_y = dy - last_dy     # Calculate derivative for PID
        speed_y = KP*dy + KI*integral_y + KD*derivative_y  # Speed Y-direction
        # Calculate motorspeed out of speed_x and speed_y
        # Use GAIN otherwise speed will be to slow,
        # but limit in range [-900,900]
        rspeed = limit_speed(GAIN*(speed_y - speed_x))
        lspeed = limit_speed(GAIN*(speed_y + speed_x))
        rmotor.run_forever(speed_sp = round(rspeed))
        lmotor.run_forever(speed_sp = round(lspeed))
        last_dx = dx                    # Set last error for x
        last_dy = dy                    # Set last error for y
    else:
        # SIG1 not detected, stop motors
        rmotor.stop()
        lmotor.stop()
        last_dx = 0
        last_dy = 0

# TouchSensor pressed, stop motors
rmotor.stop()
lmotor.stop()
