#!/usr/bin/env python3
import sys,os
import configparser
from timescale_poster import timescale_poster
#add the wave python directory to our path so that we can import the wave client
sys.path.append(os.path.join(os.path.dirname(__file__), '..','wave','python'))
import client as WaveClient

postgresParser = configparser.ConfigParser()
mqttParser = configparser.ConfigParser()
waveParser = configparser.ConfigParser()

#import the postgres config file
postgresParser.read('postgres.ini')
postgresConf = postgresParser['DEFAULT']

#import the MQTT config file
mqttParser.read('mqtt.ini')
mqttConf  = mqttParser['DEFAULT']

#import the wave config file
waveParser.read('wave.ini')
waveConf = waveParser['DEFAULT']

#initialize a timescale poster library
timescale = timescale_poster.TimescalePoster(host=postgresConf['host'], 
                            port=postgresConf['port'],
                            database=postgresConf['database'],
                            username=postgresConf['username'],
                            password=postgresConf['password'])

#startup the wave client and subscribe to all topics
on_message = None
waveClient = WaveClient.Client(entity_name=waveConf['name'],
                    wave_uri=waveConf['uri'],
                    mosquitto_url=mqttConf['host'],
                    mosquitto_pass=mqttConf['password'],
                    mosquitto_user=mqttConf['username'],
                    mosquitto_port=mqttConf['port'],
                    on_message=on_message)

waveNamespace = waveConf['namespace']
waveClient.subscribe(waveNamespace, "#")

#catch the topics and post the data to postgres
def on_message(client, userdata, message):
    print(message.topic + ':' + message.payload)

import time
while True:
    time.sleep(1)
