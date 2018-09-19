#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..','wave','python'))

import conixposter
from uuid import getnode as get_mac

# also serves as subscribe topic
a_uuid = "8608a83a-b7a2-11e8-8755-0cc47a0f7eea"

### PUBLISHER
def sensor():
    i = 0
    while True:
        i = i+1
        yield i

a_sensor = sensor()

poster = conixposter.ConixPoster(get_mac())

# sense'n'send
import threading
import time
def sense_and_send():
    while True:
        time.sleep(10)
        poster.post(a_uuid, poster.sensorTypes.ZONE_TEMPERATURE_SENSOR, next(a_sensor))
t = threading.Thread(target=sense_and_send)
t.start()
