#!/usr/bin/env python3
import sys
import os
import json
import pint
import conixposter
from uuid import getnode as get_mac

# also serves as subscribe topic
# a_uuid = "8608a83a-b7a2-11e8-8755-0cc47a0f7777"

# PUBLISHER

def sensor():
    i = 0
    while True:
        i = i+1
        yield i


a_sensor = sensor()

poster = conixposter.ConixPoster(get_mac(), wave_uri="localhost:4110")

# sense'n'send
import threading
import time


def sense_and_send():
    while True:
        line = sys.stdin.readline()
        if line == "":
            return

        decoded = json.loads(line)
        part_uuid = decoded['deviceid']
        part_value = decoded['payload']
        poster.post(part_uuid, conixposter.Sensors.Temperature, part_value, 'count')
        ureg = pint.UnitRegistry()


t = threading.Thread(target=sense_and_send)
t.start()
