#!/usr/bin/python3

import configparser
import TimescalePoster


postgresParser = configparser.ConfigParser()
mqttParser = configparser.ConfigParser()

#import the postgres config file
postgresParser.read(postgresConfig.ini)

#import the MQTT config file
mqttParser.read(mqtt.ini)

#initialize a timescale poster library
timescale = TimescalePoster(host=postgresParser['host'], 
                            port=postgresParser['port'],
                            database=postgresParser['database'],
                            username=postgresParser['username'],
                            password=postgresParser['password'])

#startup the wave client and subscribe to all topics

#catch the topics and post the data to postgres
