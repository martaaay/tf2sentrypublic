from pygame import mixer
import os
import time

from servo_config import *
import RPi.GPIO as GPIO

from Blynk import BlynkLib

BLYNK_AUTH = '' # Update me with Blynk auth code from the app

blynk = BlynkLib.Blynk(BLYNK_AUTH, server="10.0.0.2", port=8080)

os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
mixer.init()

#mixer.music.load('audio/sentry_scan.wav')
max_volume = 1.0
volume_pct = 1.0
mixer.music.set_volume(volume_pct * max_volume)
mixer.music.stop()

pusher_extended_button = 17
GPIO.setup(pusher_extended_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Move pusher until the button is off. Start True so that 
# if the pusher is touching the button it will be moved out of position
state_pusher_move_until_button_off = True
state_pusher_move_until_button_on = False

state_launcher_initial_warming_up = False
state_launcher_post_firing_warming_up = False

launcher_initial_warm_up_time = 1.0
launcher_initial_warm_up_started = 0.0 
launcher_post_firing_warm_up_time = 2.5
launcher_post_firing_warm_up_started = 0.0

# Stop pusher
pusher_motor.setToPosition(0.0)
launcher_motor.setToPosition(0.0)

DEBUG = False

for name, motor in all_motors.items():
  motor.set_debug(DEBUG)

shoot_button_pressed = False

@blynk.VIRTUAL_WRITE(0)
def shoot_button_handler(values):
  if values[0] == "0":
    shoot_button_pressed = False
    on_shoot_button_released()
  else:
    shoot_button_pressed = True
    on_shoot_button_pressed()

@blynk.VIRTUAL_WRITE(2)
def joystick_handler(values):
  x = (int(values[0])-128)/128.0
  y = (int(values[1])-128)/128.0
  yaw_servo.setToPosition((x+1.0)/2.0)
  pitch_servo.setToPosition((y+1.0)/2.0)

@blynk.VIRTUAL_WRITE(3)
def joystick_x_handler(values):
  x = (int(float(values[0]))-128)/128.0
  yaw_servo.setToPosition((x+1.0)/2.0)

@blynk.VIRTUAL_WRITE(4)
def joystick_y_handler(values):
  y = (int(float(values[0]))-128)/128.0
  pitch_servo.setToPosition((y+1.0)/2.0)

@blynk.VIRTUAL_WRITE(5)
def fire_audio_button(values):
  if values[0] != '1': return
  mixer.Channel(2).play(mixer.Sound('audio/sentry_shoot.wav'))

@blynk.VIRTUAL_WRITE(6)
def alert_audio_button(values):
  if values[0] != '1': return
  mixer.Channel(3).play(mixer.Sound('audio/sentry_spot_client.wav'))

@blynk.VIRTUAL_WRITE(7)
def out_of_ammo_audio_button(values):
  if values[0] != '1': return
  mixer.Channel(2).play(mixer.Sound('audio/sentry_empty.wav'))

@blynk.VIRTUAL_WRITE(8)
def toggle_idle_audio(values):
  if values[0] != '1': return
  if mixer.Channel(0).get_busy() or mixer.Channel(0).get_busy():
    mixer.Channel(0).stop()
    mixer.Channel(1).stop()
  else:
    mixer.Channel(0).play(mixer.Sound('audio/sentry_scan.wav'))
    channel_to_start_time[0] = time.time()
    channel_to_start_time[1] = time.time()

def on_shoot_button_pressed():
  global state_launcher_initial_warming_up
  global launcher_initial_warm_up_started

  state_launcher_initial_warming_up = True
  launcher_initial_warm_up_started = time.time()
  launcher_motor.setToPosition(0.99)

def on_shoot_button_released():
  global state_launcher_initial_warming_up
  global state_launcher_post_firing_warming_up
  global state_pusher_move_until_button_on

  state_launcher_initial_warming_up = False
  state_launcher_post_firing_warming_up = False
  state_pusher_move_until_button_on = False
  state_pusher_move_until_button_off = True
  launcher_motor.setToPosition(0.0)
  pusher_motor.setToPosition(0.0)

print("Warmed up")
channel_to_start_time = {}

channel_to_start_time[0] = time.time()

def choose_demo_pitch():
  if random.random()>0.2:
    pitch_servo.setToPosition(random.random()*0.4+0.3)

start_time = time.time()
def loop():
  global state_pusher_move_until_button_off
  global state_pusher_move_until_button_on
  global state_launcher_initial_warming_up
  global state_launcher_post_firing_warming_up
  global launcher_initial_warm_up_time
  global launcher_initial_warm_up_started
  global launcher_post_firing_warm_up_time
  global launcher_post_firing_warm_up_started
  global shoot_button_pressed
  global start_time
  global channel_to_start_time

  # Play idle sound
  if not mixer.Channel(1).get_busy() and mixer.Channel(0).get_busy() and time.time() - channel_to_start_time.get(0, 0) >= 1.5:
    mixer.Channel(1).play(mixer.Sound('audio/sentry_scan.wav'))
    channel_to_start_time[1] = time.time()
    yaw_servo.setToPosition(0.3)
    choose_demo_pitch()

  if not mixer.Channel(0).get_busy() and mixer.Channel(1).get_busy() and time.time() - channel_to_start_time.get(1, 0) >= 1.5:
    mixer.Channel(0).play(mixer.Sound('audio/sentry_scan.wav'))
    channel_to_start_time[0] = time.time()
    yaw_servo.setToPosition(0.7)
    choose_demo_pitch()

  if state_pusher_move_until_button_on:
    pusher_motor.setToPosition(0.99)

  if state_launcher_initial_warming_up and \
    launcher_initial_warm_up_started + launcher_initial_warm_up_time < time.time():
    state_launcher_initial_warming_up = False
    state_pusher_move_until_button_on = True
  elif state_launcher_post_firing_warming_up and \
    launcher_post_firing_warm_up_started + launcher_post_firing_warm_up_time < time.time():
    # Warm up complete. Fire.
    state_launcher_post_firing_warming_up = False
    state_pusher_move_until_button_on = True

  bump_all_times()

def on_connect():
  global volume_pct
  # Update server with defaults
  blynk.virtual_write(3, 128)
  blynk.virtual_write(4, 128)

  blynk.virtual_write(9, int(volume_pct*100.0))

  print("CONNECTED")

# Start Blynk (this call should never return)
blynk.set_user_task(loop, 50)
blynk.on_connect(on_connect)
blynk.run()
