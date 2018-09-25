#!/usr/bin/env python3
import sys, os
import pint
import time
import json
import conixposter
import paho.mqtt.client as mqtt
from uuid import getnode as get_mac

# Setup conix poster
poster = conixposter.ConixPoster(get_mac())

def on_connect(client, userdata, flags, rc):
    print('Connected with result ' + str(rc))
    client.subscribe("gateway-data")

def on_message(client, userdata, msg):
    print('got message')
    try:
        data = json.loads(str(msg.payload, 'utf-8'))
        device_type = data['device']
        device_id = data['_meta']['device_id']
        timestamp = data['_meta']['timestamp']
        topic = None
        if 'topic' in data:
            topic = data['topic']
        print(device_type)
        print(device_id)
        print(topic)

        if (device_type == 'gateway_metrics') :
            poster.post(device_id, conixposter.Diagnostics.Up_Time, data['uptime'], 'second', timestamp)
            poster.post(device_id, conixposter.Diagnostics.CPU_Usage, data['load']['5m'], 'count', timestamp)
            poster.post(device_id, conixposter.Diagnostics.Memory_Usage, data['mem']['total'] - data['mem']['free'], 'kilobyte', timestamp)
            poster.post(device_id, conixposter.Diagnostics.Memory_Free, data['mem']['total'], 'kilobyte', timestamp)


        if (topic == 'light_lux') :
            poster.post(device_id, conixposter.Sensors.Luminance, data[topic], 'lux', timestamp)
        elif (topic == 'light_color_cct_k') :
            poster.post(device_id, conixposter.Sensors.Light_Color_CCT, data[topic], 'kelvin', timestamp)
        elif (topic == 'motion') :
            poster.post(device_id, conixposter.Sensors.Motion, data[topic], 'count', timestamp)
        elif (topic == 'temperature_c') :
            poster.post(device_id, conixposter.Sensors.Temperature, data[topic], 'degC', timestamp)
        elif (topic == 'pressure_mbar') :
            poster.post(device_id, conixposter.Sensors.Pressure, data[topic], 'millibar', timestamp)
        elif (topic == 'humidity_percent') :
            poster.post(device_id, conixposter.Sensors.Humidity, data[topic], 'percent', timestamp)
        elif (topic == 'volt') :
            poster.post(device_id, conixposter.Diagnostics.Solar_Panel_Voltage, data['solar_voltage'], 'volt', timestamp)
            poster.post(device_id, conixposter.Diagnostics.Secondary_Battery_Voltage, data['secondary_voltage'], 'volt', timestamp)
            poster.post(device_id, conixposter.Diagnostics.Battery_Voltage, data['primary_voltage'], 'volt', timestamp)
        elif (topic == 'free_ot_buffers') :
            poster.post(device_id, conixposter.Diagnostics.Memory_Usage, 128 - data[topic], 'count', timestamp)
    except Exception as e:
        print(e)


# Initialize mqtt client
mqtt_client = mqtt.Client("coap-conix-poster")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect('localhost', 1883, 60)
mqtt_client.loop_forever()

