import conixsubscriber
import paho.mqtt
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

#setup the data callback to repost the data that we care about in the right format
def publishCallback(data):
    packet_to_publish = {}

    #set the uuid
    packet_to_publich['uuid'] = data['uuid']
    del data['uuid']

    packet_to_publich['timestamp'] = data['timestamp']
    del data['uuid']

    #set the location
    packet_to_publish['position'] = {}
    if 'location_local_x' in data:
        packet_to_publish['position']['x'] = data['location_local_x']
        del data['location_local_x']
    if 'location_local_y' in data:
        packet_to_publish['position']['y'] = data['location_local_y']
        del data['location_local_y']
    if 'location_local_z' in data:
        packet_to_publish['position']['z'] = data['location_local_z']
        del data['location_local_z']
    
    packet_to_publish['data'] = {}
    for key in data:
        if key.split('_')[-1] == 'units':
            pass
        else:
            packet_to_publish['data'][key] =str(data[key] + '_' + data[key+'_units'])
    
    print(packet_to_publish)

#subscribe to the data we care about
subscriber.subscribe(['*'],'location_origin_uuid=404', callback)
