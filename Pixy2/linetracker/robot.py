""" All code for the robot."""
from time import sleep
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from ev3dev2.port import LegoPort
from ev3dev2.sound import Sound
from ev3dev2.led import Leds


SPEED_FAST = 300
SPEED_SLOW = 100

class Robot:
    def __init__(self):
        self.sound = Sound()
        self._leds = Leds()
        # Connect TouchSensor
        self.touch_4 = TouchSensor(INPUT_4)
        # Connect motors
        self.motor_a = LargeMotor(OUTPUT_A)
        self.motor_b = LargeMotor(OUTPUT_B)
        # Connect Pixy camera
        in1 = LegoPort(INPUT_1)
        in1.mode = 'other-i2c'
        sleep(0.5)
        # State of robot
        self._ACTIVE = True
        self.activate()
        self._basic_speed = SPEED_FAST
        self._GAIN = 15

    def move(self, speed_x):
        """Move robot when in _ACTIVE mode."""
        if self._ACTIVE:
            speed_x *= self._GAIN
            speed_a = limit_speed(self._basic_speed - speed_x)
            speed_b = limit_speed(self._basic_speed + speed_x)
            self.motor_a.run_forever(speed_sp=speed_a)
            self.motor_b.run_forever(speed_sp=speed_b)
    
    def move_slow(self):
        """Set basic speed to slow."""
        self._basic_speed = SPEED_SLOW

    def move_fast(self):
        """Set basic speed to fast."""
        self._basic_speed = SPEED_FAST

    def stop(self):
        """Stop robot."""
        self.motor_a.off()
        self.motor_b.off()

    def activate(self):
        """Set robot status to active."""
        self._ACTIVE = True
        self.set_leds_default()

    def deactivate(self):
        """Set robot status to in-active."""
        self._ACTIVE = False
        self.stop()
        self._leds.set_color('LEFT', 'RED')
        self._leds.set_color('RIGHT', 'RED')

    def set_leds_right(self):
        self._leds.set_color('RIGHT', 'ORANGE')

    def set_leds_left(self):
        self._leds.set_color('LEFT', 'ORANGE')

    def set_leds_default(self):
        self._leds.all_off()
        self._leds.set_color('RIGHT', 'GREEN')
        self._leds.set_color('LEFT', 'GREEN')


def limit_speed(speed):
  """Limit speed in range [-900,900]."""
  if speed > 900:
    speed = 900
  elif speed < -900:
    speed = -900
  return speed
