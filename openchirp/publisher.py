#!/usr/bin/env python3
import sys
import os
import json
import pint
import conixposter as cp
from uuid import getnode as get_mac

poster = cp.ConixPoster(get_mac(), wave_uri="localhost:4110")

ureg = pint.UnitRegistry()

defaultsensor = (cp.Sensors.Temperature, 'count')
topic2sensor = {
    "rawtx": defaultsensor,
    "rawrx": defaultsensor,
    "joinrequest": defaultsensor,
    "battery": (cp.Sensors.Battery_Voltage, ureg.get_name('volt')),
    "counter": defaultsensor,
    "gas":  (cp.Sensors.Relative_Humidity, ureg.get_name('ohm')),
    "humidity": (cp.Sensors.Relative_Humidity, 'percent'),
    "light": defaultsensor,
    "pressure": defaultsensor,
    "pir": (cp.Sensors.PIR, 'count'),
    "motion": defaultsensor,
    "lightenabled": defaultsensor,
    "micenabled": defaultsensor,
    "motionenabled": defaultsensor,
    "rate": defaultsensor,
    "set_lightenabled": defaultsensor,
    "set_micenabled": defaultsensor,
    "set_motionenabled": defaultsensor,
    "set_rate": defaultsensor,
    "temperature": defaultsensor,
    "temperature_f": defaultsensor,
    "temp_top": (cp.Sensors.Water_Heater_Temperature_Top, ureg.get_name('degF')),
    "temp_bottom": (cp.Sensors.Water_Heater_Temperature_Bottom, ureg.get_name('degF'))
}

# sense'n'send
import threading
import time


def match_sensor_units(topic):
    return topic2sensor.get(topic, defaultsensor)


def sense_and_send():
    while True:
        line = sys.stdin.readline()
        if line == "":
            return

        decoded = json.loads(line)
        part_uuid = decoded['deviceid']
        part_topic = decoded['topic']
        part_value = decoded['payload']

        sensor_type, sensor_units = match_sensor_units(part_topic)
        poster.post(part_uuid, sensor_type, part_value, sensor_units)


t = threading.Thread(target=sense_and_send)
t.start()
