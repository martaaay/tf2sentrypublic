import time

import maestro

dev = '/dev/serial0'
servo = maestro.Controller(dev)

servo.setAccel(0,0)      #set servo 0 acceleration to 4
servo.setSpeed(0,0)      #set servo 0 acceleration to 4

servo.setTarget(0,6000)

servo.close()
