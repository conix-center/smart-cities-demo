#!/usr/bin/env python3

import conixsubscriber
import paho.mqtt.client as mqtt
import configparser
import json
import datetime

#import the postgres config file
postgresParser = configparser.ConfigParser()
postgresParser.read('postgres.ini')
postgresConf = postgresParser['DEFAULT']

#setup a subscriber
subscriber = conixsubscriber.ConixSubscriber("ar_demo_gateway",
                                            database_username = postgresConf['username'],
                                            database_port = postgresConf['port'],
                                            database_name = postgresConf['database'],
                                            database_password = postgresConf['password'],
                                            database_host = postgresConf['host'])


def onConnect():
    print('Other client Connected!')

#setup an mqtt instance
mqttclient = mqtt.Client(client_id='ardemo-gateway', clean_session=True)
mqttclient.on_connect = onConnect
mqttclient.connect('localhost', 1883, 60)
mqttclient.loop_start()

#setup the data callback to repost the data that we care about in the right format
def publishCallback(data):
    
    if 'memory_usage' not in data or 'cpu_usage' not in data:
        return

    packet_to_publish = {}

    #set the uuid
    packet_to_publish['uuid'] = data['uuid']

    packet_to_publish['last update'] = datetime.datetime.utcfromtimestamp(data['timestamp']/1000000).strftime("%H:%M:%S")

    #set the location
    packet_to_publish['position'] = {}
    if 'location_local_x' in data:
        packet_to_publish['position']['x'] = data['location_local_x']
    if 'location_local_y' in data:
        packet_to_publish['position']['y'] = data['location_local_y']
    if 'location_local_z' in data:
        packet_to_publish['position']['z'] = data['location_local_z']

    packet_to_publish['data'] = {}
    ignore_list = ['uuid','timestamp','location_local_x','location_local_z','location_local_y','location_origin_uuid']
    for key in data:
        if key in ignore_list:
            continue

        if key.split('_')[-1] == 'units':
            pass
        else:
            name_str = None
            try:
                name_float = float(data[key])
                name_str = "{}".format(name_float)
            except:
                try:
                    name_int = int(data[key])
                    name_str = "{}".format(name_int)
                except:
                    name_str = data[key]

            if str(data[key+'_units']) == 'percent':
                packet_to_publish['data'][key] = name_str + " %"
            elif str(data[key+'_units']) == 'count':
                packet_to_publish['data'][key + ' count'] = name_str
            elif str(data[key+'_units']) == 'boolean':
                packet_to_publish['data'][key] = name_str
            else:
                packet_to_publish['data'][key] = name_str + ' ' + str(data[key+'_units'])

    print(packet_to_publish)
    mqttclient.publish('ardemo',payload=json.dumps(packet_to_publish))

#subscribe to the data we care about
subscriber.subscribe(['location_local_x','location_local_y','location_local_z','Memory_Usage','memory_usage_units','cpu_usage','cpu_usage_units'],'location_origin_uuid=404', publishCallback)

import time
while True:
    time.sleep(1)
