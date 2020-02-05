import random
import time

import RPi.GPIO as GPIO
from board import SCL, SDA
import busio

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685

# This example also relies on the Adafruit motor library available here:
# https://github.com/adafruit/Adafruit_CircuitPython_Motor
from adafruit_motor import servo

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

i2c = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c)
pca.frequency = 50

all_motors = {}

class MotorDef:
  def setToPosition(self, pos): # pos is from 0.0 to 1.0
    raise Exception("Unimplemented base")

  def bump_time(self):
    raise Exception("Unimplemented base")

  def relax(self):
    raise Exception("Unimplemented base")

  def set_debug(self, debug_mode):
    raise Exception("Unimplemented base")

class ServoDef(MotorDef):
  def __init__(self, name, num, speed, min, max, initial_position):
    dev = '/dev/serial0'
    self.servo = servo.Servo(pca.channels[num], min_pulse=min, max_pulse=max)
    self.debug = False

    self.speed = speed
    self.name = name
    self.num = num
    self.min = min
    self.max = max
    print("Servo %s setup with min: %s and max: %s" % (num, min, max))
    self.target_position = None
    self.current_position = None
    self.last_time = None

    all_motors.update({name: self})
    self.setToPosition(initial_position, fastest=True)

  def set_debug(self, debug_mode):
    self.debug = debug_mode

  def setToPosition(self, pos, fastest=False): # pos is from 0.0 to 1.0
    if pos < 0.0 or pos > 1.0:
      return

    if self.debug:
      print("Servo %s set to %s" % (self.name, pos))
      return

    self.target_position = pos
    if fastest or self.speed == 0:
      self.current_position = pos
      self.servo.fraction = pos
      return

  def relax(self):
    pass
    #self.servo.setTarget(0, 0)

  def bump_time(self):
    if self.speed == 0: return
    if self.last_time is None:
      self.last_time = time.time()
      return
    if self.target_position > self.current_position:
      new_fraction = self.current_position + (time.time()-self.last_time)*self.speed
      if self.target_position < new_fraction:
        self.current_position = self.target_position
      else:
        self.current_position = new_fraction
    elif self.target_position < self.current_position:
      new_fraction = self.current_position - (time.time()-self.last_time)*self.speed
      if self.target_position > new_fraction:
        self.current_position = self.target_position
      else:
        self.current_position = new_fraction
    self.last_time = time.time()
    self.servo.fraction = self.current_position

class DCMotorDef(MotorDef):
  def __init__(self, name, motorAPin, motorBPin):
    GPIO.setup(motorAPin, GPIO.OUT)
    GPIO.setup(motorBPin, GPIO.OUT)
    self.motorAPin = motorAPin
    self.motorBPin = motorBPin
    self.debug = False

    self.name = name
    print("Motor %s setup on pin %s and %s" % (name, motorAPin, motorBPin))

    all_motors.update({name: self})

  def set_debug(self, debug_mode):
    self.debug = debug_mode

  def setToPosition(self, pos): # pos is from 0.0 to 1.0
    if pos < 0.0 or pos > 1.0:
      return

    if pos < 0.5:
      GPIO.output(self.motorAPin, GPIO.LOW)
      GPIO.output(self.motorBPin, GPIO.LOW)
    else:
      GPIO.output(self.motorAPin, GPIO.HIGH)
      GPIO.output(self.motorBPin, GPIO.LOW)

  def relax(self):
    self.setToPosition(0.0)

  def bump_time(self):
    pass

pitch_servo = ServoDef("pitch_servo", 0, 0, 900, 2200, 0.5)
yaw_servo = ServoDef("yaw_servo", 9, 0.25, 1000, 2200, 0.5)
launcher_motor = ServoDef("launcher_motor", 2, 0, 0, 20000, 0.0)
pusher_motor = ServoDef("pusher_motor", 3, 0, 0, 20000, 0.0)

def bump_all_times():
  for name, servo in all_motors.items():
    servo.bump_time()
