#!/usr/bin/env python3
''' Demo how to use Pixy for LEGO Mindstorms on the ev3dev operating system.

    This is a simple Python demo to show how to use the Pixy camera
    on the ev3dev operating system.

    NOTE: this demo is for the first version of Pixy for LEGO Mindstorms.
          Use pixy2_demo.py for Pixy2 for LEGO Mindstorms.

    Requirements:
        Hardware: - LEGO EV3-brick
                  - Pixy for LEGO Mindstorms, attached to input port 1
                    Set Pixy to detect signature 1 (see documentation Pixy2)
                  - LEGO TouchSensor, attached to input port 4
        Software: - ev3dev operating system


    Kees Smit, 2019
    github:  github.com/KWSmit
    website: kwsmit.github.io
'''

from time import sleep

from ev3dev2.display import Display
from ev3dev2.sensor import Sensor, INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.port import LegoPort


# EV3 Display
lcd = Display()

# Connect TouchSensor
ts = TouchSensor(INPUT_4)

# Set LEGO port for Pixy on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'auto'
# Wait 2 secs for the port to get ready
sleep(2)

# Connect Pixy camera
pixy = Sensor(INPUT_1)
# Set mode to detect signature 1 only
pixy.mode = 'SIG1'

# Read and display data until TouchSensor is pressed
while not ts.value():
    # Clear EV3 display
    lcd.clear()
    # Read values from Pixy
    x = pixy.value(1)     # X-coordinate of centerpoint of object
    y = pixy.value(2)     # Y-coordinate of centerpoint of object
    w = pixy.value(3)     # Width of rectangle around detected object
    h = pixy.value(4)     # Heigth of rectangle around detected object
    # scale to resolution of EV3 display:
    # Resolution Pixy while color tracking; (255x199)
    # Resolution EV3 display: (178x128)
    x *= 0.7
    y *= 0.6
    w *= 0.7
    h *= 0.6
    # Calculate reactangle to draw on EV3-display
    dx = int(w/2)         # Half of the width of the rectangle
    dy = int(h/2)         # Half of the height of the rectangle
    xa = x - dx           # X-coordinate of top-left corner
    ya = y + dy           # Y-coordinate of the top-left corner
    xb = x + dx           # X-coordinate of bottom-right corner
    yb = y - dy           # Y-coordinate of the bottom-right corner
    # Draw rectangle on display
    lcd.draw.rectangle((xa, ya, xb, yb), fill='black')
    # Updats display to show rectangle
    lcd.update()
