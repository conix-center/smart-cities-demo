#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'conixsubscriber'))
import conixsubscriber
import configparser

#import the postgres config file
postgresParser = configparser.ConfigParser()
postgresParser.read('postgres.ini')
postgresConf = postgresParser['DEFAULT']

subscriber = conixsubscriber.ConixSubscriber("subscribe",
                                            database_username = postgresConf['username'],
                                            database_port = postgresConf['port'],
                                            database_name = postgresConf['database'],
                                            database_password = postgresConf['password'],
                                            database_host = postgresConf['host'])

def callback(data):
    print(data)

subscriber.subscribe(['Temperature','temperature_units'],'cpu_usage > 49.9', callback)

import time
while True:
    time.sleep(1)
