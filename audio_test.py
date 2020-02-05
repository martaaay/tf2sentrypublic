from pygame import mixer
import os
import time


os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
mixer.init()

mixer.music.load('audio/sentry_scan.wav')
mixer.music.set_volume(1.0)
mixer.music.play()

while mixer.music.get_busy():
  time.sleep(.1)
