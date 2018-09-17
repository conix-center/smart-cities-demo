#!/usr/bin/env python3
import sys,os
import configparser
from timescale_poster import timescale_poster
#add the wave python directory to our path so that we can import the wave client
sys.path.append(os.path.join(os.path.dirname(__file__), '..','wave','python'))
import client as WaveClient
import datetime

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

#catch the topics and post the data to postgres
def message(client, userdata, message):
    # Every sensor channel has a UUID
    # We also expect actuators do do things like report state
    # Therefore each UUID is bidirectional so we expect a structure like: UUID/send or UUID/receive
    # We also accept metadata about a channel. Metadata *is not* other sensor readings, but instead
    # things like the UUID of the sending sensor, information about accuracy/precision, the gateway which forwarded the data.
    # We also expect all data to have a timestamp, if not we will add one
    # So in this light:

    # Extract the topic and the subtopic to use as a table name
    # If no subtopic exists then just use the topic as the table name
    topics = message.topic.split('/')
    tableName = None
    if(len(topics) == 2):
        tableName = topics[1]
    elif(len(topics) >= 3):
        tableName = topics[1] + '-' + topics[2]

    # Look for a timestamp in the message. If none exists use now as the time
    #lowercase the message dict
    payload_lower = {k.lower():v for k,v in message.payload.items()}

    timescale_timestamp = None
    if 'time' in payload_lower:
        timescale_timestamp = payload_lower['time']
        del payload_lower['time']
    elif timestamp in payload_lower:
        timescale_timestamp = payload_lower['timestamp']
        del payload_lower['timestamp']
    elif tstamp in payload_lower:
        timescale_timestamp = payload_lower['tstamp']
        del payload_lower['tstamp']
    else:
        timescale_timestamp = str(datetime.datetime.now())

    # Now insert this data into timescale. If a table or row does not
    # Exist the library should handle posting it
    print("Posting to table: %s\nTimestamp: %s\nData: %s\n\n".format(tableName, timescale_timestamp, payload_lower))
    try:
        timescale.insertData(tableName, timescale_timestamp, payload_lower)
    except Exception as e:
        print("Timescale data insert failed: %s".format(e))

#startup the wave client and subscribe to all topics
waveClient = WaveClient.Client(entity_name=waveConf['name'],
                    wave_uri=waveConf['uri'],
                    mosquitto_url=mqttConf['host'],
                    mosquitto_pass=mqttConf['password'],
                    mosquitto_user=mqttConf['username'],
                    mosquitto_port=mqttConf['port'],
                    mosquitto_tls = False,
                    on_message=message)

waveNamespace = waveConf['namespace']
waveClient.subscribe(waveNamespace, "#")

import time
while True:
    time.sleep(1)
