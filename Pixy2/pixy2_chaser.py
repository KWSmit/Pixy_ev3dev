#!/usr/bin/env python3
''' Demo how your robot can follow an object with Pixy2 for LEGO Mindstorms.

    NOTE: this demo ifs for the Pixy2 for LEGO Mindstorms.
          Use pixy_chaser.py for the first version of Pixy for LEGO Mindstorms.

    Requirements:
        Hardware: - LEGO EV3-brick.
                  - Pixy2 for LEGO Mindstorms, attached to input port 1.
                    Set Pixy2 to detect signature 1 (see documentation Pixy2).
                  - Use PixyMon for setting up I2C interface.
                    I2C Address = 0x54.
                  - LEGO TouchSensor, attached to input port 4.
                  - Two LEGO LargeMotors, attached to output ports A and B.
        Software: - ev3dev operating system.
                  - Python module smbus (already available in ev3dev).

    Kees Smit, 2019
    github:  github.com/KWSmit
    website: kwsmit.github.io
'''

from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from ev3dev2.port import LegoPort
from smbus import SMBus
from time import sleep


def limit_speed(speed):
    """ Limit speed in range [-1000,1000] """
    if speed > 1000:
        speed = 1000
    elif speed < -1000:
        speed = -1000
    return speed

# Set LEGO port for Pixy2 on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'other-i2c'
sleep(0.5)

# Settings for I2C (SMBus(3) for INPUT_1)
bus = SMBus(3)
# Make sure the same address is set in Pixy2
address = 0x54

# Signatures we're interested in (SIG1)
sig = 1

# Connect TouchSensor (to stop script)
ts = TouchSensor(INPUT_4)

# Connect LargeMotors
rmotor = LargeMotor(OUTPUT_A)
lmotor = LargeMotor(OUTPUT_B)

# Defining constants
X_REF = 158  # X-coordinate of referencepoint
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
    # Request block
    bus.write_i2c_block_data(address, 0, data)
    # Read block
    block = bus.read_i2c_block_data(address, 0, 20)
    if sig == block[7]*256 + block[6]:
        # SIG1 detected, control motors
        x = block[9]*256 + block[8]   # X-centroid of largest SIG1-object
        y = block[11]*256 + block[10] # Y-centroid of largest SIG1-object
        dx = X_REF - x                # Error in reference to X_REF
        integral_x = integral_x + dx  # Calculate integral for PID
        derivative_x = dx - last_dx   # Calculate derivative for PID
        speed_x = KP*dx + KI*integral_x + KD*derivative_x  # Speed X-direction
        dy = Y_REF - y                # Error in reference to Y_REF
        integral_y = integral_y + dy  # Calculate integral for PID
        derivative_y = dy - last_dy   # Calculate derivative for PID
        speed_y = KP*dy + KI*integral_y + KD*derivative_y  # Speed Y-direction
        # Calculate motorspeed out of speed_x and speed_y
        # Use GAIN otherwise speed will be to slow,
        # but limit in range [-1000,1000]
        rspeed = limit_speed(GAIN*(speed_y - speed_x))
        lspeed = limit_speed(GAIN*(speed_y + speed_x))
        rmotor.run_forever(speed_sp = round(rspeed))
        lmotor.run_forever(speed_sp = round(lspeed))
        last_dx = dx                  # Set last error for x
        last_dy = dy                  # Set last error for y
    else:
        # SIG1 not detected, stop motors
        rmotor.stop()
        lmotor.stop()
        last_dx = 0
        last_dy = 0

# TouchSensor pressed, stop motors
rmotor.stop()
lmotor.stop()
