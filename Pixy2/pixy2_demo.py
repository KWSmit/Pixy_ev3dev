#!/usr/bin/env python3
''' Demo how to Pixy2 for LEGO Mindstorms on the ev3dev operating system.

    This is a simple Python demo to show how to use the Pixy2 camera
    on the ev3dev operating system.

    NOTE: this demo ifs for the Pixy2 for LEGO Mindstorms.
          Use pixy_demo.py for the first version of Pixy for LEGO Mindstorms.

    In contrast to the first version of Pixy for LEGO Mindstorms, you cannot
    use Pixy2 directly in ev3dev. However, you can talk to Pixy2 over I2C 
    by using the "msbus" Python module.

    Requirements:
        Hardware: - LEGO EV3-brick.
                  - Pixy2 for LEGO Mindstorms, attached to input port 1.
                    Set Pixy2 to detect signature 1 (see documentation Pixy2).
                  - Use PixyMon for setting up I2C interface.
                    I2C Address = 0x54.
                  - LEGO TouchSensor, attached to input port 4.
        Software: - ev3dev operating system.
                  - Python module smbus (already available in ev3dev).

    Kees Smit, 2019
    github:  github.com/KWSmit
    website: kwsmit.github.io
'''

from ev3dev2.display import Display
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.port import LegoPort

from smbus import SMBus
from time import sleep

# EV3 Display
lcd = Display()

# Connect ToucSensor
ts = TouchSensor(INPUT_4)

# Set LEGO port for Pixy2 on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'other-i2c'
sleep(0.5)

# Settings for I2C (SMBus(3) for INPUT_1)
bus = SMBus(3)
# Make sure the same address is set in Pixy2
address = 0x54

# Signatures we're interested in (SIG1)
sigs = 1

# Data for requesting block
data = [174, 193, 32, 2, sigs, 1]

# Read and display data until TouchSensor is pressed
while not ts.value():
    # Clear display
    lcd.clear()
    # Request block
    bus.write_i2c_block_data(address, 0, data)
    # Read block
    block = bus.read_i2c_block_data(address, 0, 20)
    # Extract data
    sig = block[7]*256 + block[6]
    x = block[9]*256 + block[8]
    y = block[11]*256 + block[10]
    w = block[13]*256 + block[12]
    h = block[15]*256 + block[14]
    # Scale to resolution of EV3 display:
    # Resolution Pixy2 while color tracking; (316x208)
    # Resolution EV3 display: (178x128)
    x *= 0.6
    y *= 0.6
    w *= 0.6
    h *= 0.6
    # Calculate rectangle to draw on display
    dx = int(w/2)
    dy = int(h/2)
    xa = x - dx
    ya = y + dy
    xb = x + dx
    yb = y - dy
    # Draw rectangle on display
    lcd.draw.rectangle((xa, ya, xb, yb), fill='black')
    # Update display to how rectangle
    lcd.update()
