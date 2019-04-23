# Tutorial how to use Pixy and Pixy2 on ev3dev operating system

This tutorial contains explanation and sample code on how to use
Pixy and Pixy2 for LEGO Mindstorms on the ev3dev operating system.

> ## Tabel of contents
> 1. [Pixy for LEGO Mindstorms](#pixy-for-lego-mindstorms)
>> - [Example 1 - Displaying detected object on EV3-LCD with Pixy](#example-1---displaying-detected-object-on-ev3-lcd-with-pixy)
>> - [Example 2 - Chasing an object with Pixy](#example-2---chasing-an-object-with-pixy)
> 2. [Pixy2 for LEGO Mindstorms](#pixy2-for-lego-mindstorms)
>> - [Example 3 - Displaying detected object on EV3-LCD with Pixy2](#example-3---displaying-detected-object-on-ev3-lcd-with-pixy2)
>> - [Example 4 - Chasing an object with Pixy2](#example-4---chasing-an-object-with-pixy2)
> 3. [Useful links](#useful-links)
---

The Pixy camera comes with its own tool: PixyMon. This tool helps you to set
the signatures (objects you want Pixy to detect) and the interface. To use
this tool you need to connect the camera directly to your PC by using a mini
USB cable. For this you can use the USB cable of your EV3.

> Notice for Pixy: <br>Beware that when PixyMon is running on your PC and the
> camera is plugged in to your PC, its values are not updated to the EV3.
> So before starting your script be sure PixyMon is not running!
> <br>This only relates to Pixy and not to Pixy2.

## Pixy for LEGO Mindstorms

This chapter explains how to use the first version of Pixy for LEGO Mindstorms.
General information about Pixy can be found at the
[Pixy-wiki](https://docs.pixycam.com/)

### The basics

First, set the input port (in this case INPUT_1) in the right mode:
```python
from ev3dev2.port import LegoPort

# Set LEGO port for Pixy on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'auto'
sleep(2)
```
The `sleep` command is needed to give the EV3-brick time to set the port
properly.

Use the `Sensor` class to connect the Pixy to EV3:
```python
from ev3dev2.sensor import Sensor, INPUT_1

pixy = Sensor(INPUT_1)
```
Next set the mode for the camera:
```python
pixy.mode = 'ALL'
```
The Pixy camera has the following modes:
- `ALL`: the camera searches for all signatures you’ve set for it.
- `SIGn`: the camera searches for signature #n (n=1 to 7).

The data which you retrieve from the camera depends on the camera mode.
You can find detailed information on [this page](http://docs.ev3dev.org/projects/lego-linux-drivers/en/ev3dev-stretch/sensor_data.html#pixy-lego).
We will explain it to you with some examples.

When the mode is set to `ALL`, you can retrieve data as follows:
```python
sig = pixy.value(1)*256 + pixy.value(0)   # Signature of largest object
x_centroid = pixy.value(2)                # X-centroid of largest SIG1-object
y_centroid = pixy.value(3)                # Y-centroid of largest SIG1-object
width = pixy.value(4)                     # Width of the largest SIG1-object
height = pixy.value(5)                    # Height of the largest SIG1-object
```
When mode is set to one of the signatures (e.g. `SIG1`), retrieve data as follows:
```python
count = pixy.value(0)          # The number of objects that match signature 1
x = pixy.value(1)              # X-centroid of the largest SIG1-object
y = pixy.value(2)              # Y-centroid of the largest SIG1-object
w = pixy.value(3)              # Width of the largest SIG1-object
h = pixy.value(4)              # Height of the largest SIG1-object
```

> Be aware that the resolution of the Pixy camera and the resolution of the
> EV3 display are not the same. Pixy's resolution is (255x199) and EV3's
> resolution is (178x128). This means you have to scale the values from
> the pixy!

### Example 1 - Displaying detected object on EV3-LCD with Pixy

Sourcecode: /Pixy/pixy_demo.py

In this example Pixy is set to mode `SIG1`. The program continuousy reads data
from the camera, until the TouchSensor is pressed. When valid data is received,
the program calculates the size and shape of the bouncing box of the largest
detected `SIG1` object. To update the bouncing box on the display, first the
display needs to be cleared and than the bouncing box can be redrawn.

Video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/b2LZpY1qbKE" frameborder="0" allowfullscreen></iframe>


### Example 2 - Chasing an object with Pixy

Sourcecode: /Pixy/pixy_chaser.py

This example uses a robot with Pixy and two LargeMotors. It is programmed to
follow an object. To understand what is happening in this program, read the
tutorial about the LEGO chase demo on the
[Pixi wiki](https://docs.pixycam.com/wiki/doku.php?id=wiki:v1:lego_chase_demo).

Video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/cDimWUEDwPU" frameborder="0" allowfullscreen></iframe>

---

## Pixy2 for LEGO Mindstorms

This chapter explains how to use the new Pixy2 for LEGO Mindstorms.

### The basics

One important difference with the old Pixy is that you have to use Pixy2
without a driver. An easy way to do this is is by using the Python `smbus`
module for setting up direct `I2C` communication between the EV3 and
the Pixy2.

First configure Pixy2 to communicate over `I2C`. For this you can use the
PixyMon tool that comes with Pixy2. Open the configure dialog and click
on the `Interface` tab.

![PixyMon configure dialog](/Images/PixyMon_configure.png)

Set `Data out port` to `I2C` and `I2C addres`
to `0x54` (or any other address you like).

In your Python script import the module `smbus`
```python
from smbus import SMBus
```

Next set the EV3 input port to `'other-i2c'`:
```python
# Set LEGO port for Pixy2 on input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'other-i2c'
sleep(0.5)
```

Define the IC2-bus:
- for `INPUT_1`: SMBus(3)
- for `INPUT_2`: SMBus(4)
- for `INPUT_3`: SMBus(5)
- for `INPUT_4`: SMBus(6)

Assume we're using port 1. Don't forget to use the same address
as configured on the Pixy2:
```python
# Settings for I2C (SMBus(3) for INPUT_1)
bus = SMBus(3)
address = 0x54
```

Now everything is set up to request and receive data form Pixy2. You
can find the serial protocol on the
[Pixy2 wiki](https://docs.pixycam.com/wiki/doku.php?id=wiki:v2:porting_guide)

Each request starts with the same two bytes `175, 193`. The other bytes
depend on the type of request. For instance, when you want to request the
firmware version of the camera, your data packet will be:
```python
data = [174, 193, 14, 0]
```

You send this request to the camera as follows:
```python
bus.write_i2c_block_data(address, 0, data)
```

Now you can read the response:
```python
block = bus.read_i2c_block_data(address, 0, 13)
```
The first parameter in this read function is the I2C-address of
the camera. The second parameter is an offset, which we don't need, so
set it to `0`. The third parameter is the number of bytes that the
response contains. As you can see in the Pixy2 documentation, the version
request returns 13 bytes. According to the documentation
you find the major version in byte 8 and the minor in byte 9:
```python
print('Firmware version: {}.{}\n'.format(str(block[8]), str(block[9])))
```

### Example 3 - Displaying detected object on EV3-LCD with Pixy2

Sourcecode: /Pixy2/pixy2_demo.py

This is the same as exmple 1, but this time with the Pixy2. We like to detect
objects with signature 1 and display the bouncing box on the display of the
EV3. For this we use `getBlocks()` to receive information about the detected
object. The data packet for the request is like this:
```python
data = [174, 193, 32, 2, sigs, 1]
```
Where `sigs` is the signature or signatures we're interested in. It is the
sum of all desired signatures. So in case we're only interested in signature 1
`sigs = 1` and when we're interested in signatures 1, 2 and 3, then
`sig = 6` (1 + 2 + 3 = 6). In this example `sigs = 1`.

We're only interested in the largest detected object with singature 1, so
the last byte of out data packet has the value 1. To read a data block we
use:
```python
# Request block
bus.write_i2c_block_data(address, 0, data)
# Read block
block = bus.read_i2c_block_data(address, 0, 20)
```
The response contains 20 bytes, hence the last parameter in
`read_i2c_block_data()` is `20`. Now we can extract the desired data:
```python
x = block[9]*256 + block[8]
y = block[11]*256 + block[10]
w = block[13]*256 + block[12]
h = block[15]*256 + block[14]
```
With this information we can calculate and diplay the bouncing box, just like
in example 1.

> Be aware that the resolution of the Pixy2 camera and the resolution of the
> EV3 display are not the same. Pixy2's resolution while color tracking is
> (316x208) and EV3's resolution is (178x128). This means you have to scale
> the values from the Pixy2!


Video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/Wo6f2eQZVSY" frameborder="0" allowfullscreen></iframe>

### Example 4 - Chasing an object with Pixy2

Sourcecode: /Pixy2/pixy2_chaser.py

This is the same as example 2, but this time for Pixy2. It's pretty
straightforwarded when you understand the previous examples.

Video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/iy7fy2fAHsc" frameborder="0" allowfullscreen></iframe>

---

## Useful links

- ev3dev: [www.ev3dev.org](https://www.ev3dev.org)
- Pixy/Pixy2 general information: [www.pixycam.com](https://www.pixycam.com)
- Pixy/Pixy2 documentation: [docs.pixycam.com](https://docs.pixycam.com)
- my website: [Robots & More](https://kwsmit.github.io)
