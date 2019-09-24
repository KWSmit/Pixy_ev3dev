#!/usr/bin/env python3
from math import degrees, atan2
from time import sleep

from pixy2 import (
    Pixy2,
    MainFeatures,
    parse_main_features,
    BARCODE_DEACTIVATE,
    BARCODE_ACTIVATE,
    BARCODE_FORWARD,
    BARCODE_LEFT,
    BARCODE_RIGHT,
    )
from robot import Robot

# Defining constants
X_REF = 39   # X-center coordinate of view
Y_REF = 25   # Y-center coordinate of view
KP = 0.6     # Proportional constant PID-controller
KI = 0.0     # Integral constant PID-controller
KD = 0.0     # Derivative constant PID-controller

ev3 = Robot()
pixy2 = Pixy2()
data = MainFeatures()
start_intersection = False

# Initializing PID variables
integral_x = 0
derivative_x = 0
last_dx = 0

# Toggle lamp pixy on
pixy2.lamp_on()

# Loop until TouchSensor is pressed
while not ev3.touch_4.value():
    # Get raw data form pixy2
    raw_data = pixy2.getdata()
    # Parse data
    data = parse_main_features(raw_data)
    # Process data
    if data.number_of_barcodes > 0:
        # Barcode(s) found
        for i in range(0, data.number_of_barcodes):
            if data.barcodes[i].code == BARCODE_ACTIVATE:
                ev3.activate()
            elif data.barcodes[i].code == BARCODE_DEACTIVATE:
                ev3.deactivate()
            elif data.barcodes[i].code == BARCODE_RIGHT:
                pixy2.set_next_turn(-90)
                ev3.set_leds_right()
            elif data.barcodes[i].code == BARCODE_LEFT:
                pixy2.set_next_turn(90)
                ev3.set_leds_left()
    if data.number_of_intersections > 0:
        # Intersection found
        ev3.sound.beep()
    if data.number_of_vectors > 0:
        # Check for intersection
        if data.vectors[0].flags == 4:
            # Intersection in sight, so slow down not to miss it
            ev3.move_slow()
            start_intersection = True
        else:
            # No intersection in sight, so fulll speed ahead
            ev3.move_fast()
            if start_intersection:
                start_intersection = False
                ev3.set_leds_default()
        # Calculate speed out of offset in X-coördinate, using PID
        dx = X_REF - data.vectors[0].x1
        integral_x += dx
        derivative_x = dx -last_dx
        speed_x = KP*dx + KI*integral_x + KD*derivative_x
        last_dx = dx
        ev3.move(speed_x)
    else:
        # No data, stop robot
        ev3.stop()

    data.clear()

# Toggle lamp off
pixy2.lamp_off()

# Stop robot
ev3.stop()
