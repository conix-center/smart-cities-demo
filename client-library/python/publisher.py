#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..','wave','python'))
import client
import configparser

#import the MQTT config file
mqttParser = configparser.ConfigParser()
mqttParser.read('mqtt.ini')
mqttConf  = mqttParser['DEFAULT']

# also serves as subscribe topic
a_uuid = "8608a83a-b7a2-11e8-8755-0cc47a0f7eea"

### PUBLISHER
def sensor():
    i = 0
    while True:
        i = i+1
        yield i

a = client.Client("b",
        mosquitto_url=mqttConf['host'],
        mosquitto_pass=mqttConf['password'],
        mosquitto_user=mqttConf['username'],
        mosquitto_port=mqttConf['port'],
        mosquitto_tls = True)

print("entity is", a.b64hash)
a_sensor = sensor()
namespace = a.register(a_uuid)

# "out of band" a grants to b
# TODO: replace this with the b64 hash you get for the 'b' entity upon running 'subscriber.py', then uncomment this
# b_entity = "GyDIik10v8Qbh9queY86HESpqLNWBy6d2lGL_Tq6NQDwDw=="
# a.grant_read_to(b_entity, client.smart_cities_namespace, a_uuid+'/*')

# sense'n'send
import threading
import time
def sense_and_send():
    while True:
        time.sleep(10)
        a.publish(namespace, a_uuid + '/sensor', {'uuid': a_uuid, 'count': next(a_sensor)})
t = threading.Thread(target=sense_and_send)
t.start()
