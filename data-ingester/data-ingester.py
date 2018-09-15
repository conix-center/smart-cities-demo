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
postgresParser.read(postgres.ini)

#import the MQTT config file
mqttParser.read(mqtt.ini)

#import the wave config file
waveParser.read(wave.ini)

#initialize a timescale poster library
timescale = TimescalePoster(host=postgresParser['host'], 
                            port=postgresParser['port'],
                            database=postgresParser['database'],
                            username=postgresParser['username'],
                            password=postgresParser['password'])

#startup the wave client and subscribe to all topics
on_message = None
waveClient = WaveClient(entity_name=waveParser['name'],
                    wave_uri=waveParser['uri'],
                    mosquitto_url=mqttParser['host'],
                    mosquitto_pass=mqttParser['password'],
                    mosquitto_user=mqttParser['username'],
                    on_message=on_message)

waveNamespace = waveParser['namesapce']
waveClient.subscribe(waveNamespace, "#")

#catch the topics and post the data to postgres
def on_message(client, userdata, message):
    print(message.topic + ':' + message.payload)
