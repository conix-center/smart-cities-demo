#!/usr/bin/env python3
import sys
import os
from multiprocessing import Process, Queue
import json
import pint
import conixposter as cp
from uuid import getnode as get_mac

unknowns_file = "unknown_topics.txt"

undefinedtopics = {}
def addunknowntopic(deviceid, topic):
    if topic in undefinedtopics:
        return

    undefinedtopics[topic] = True
    topics = undefinedtopics.keys()
    with open(unknowns_file, "w") as f:
        f.write('\n'.join(topics))
        f.write('\n')

def interpret_bool(input):
    return bool(input)

def interpret_onoff(input):
    if bool(input):
        return 'On'
    else:
        return 'Off'

defaultsensor = None
topic2sensor = {
    # LoRaWAN Devices
    "rawtx": None,
    "rawrx": None,
    "joinrequest": (cp.Diagnostics.Network_Join_Indication, 'boolean'),

    # SensorBug
    "battery": (cp.Sensors.Battery_Voltage, 'volt'),
    "counter": (cp.Diagnostics.Packet_Count, 'count'),
    "gas":  (cp.Sensors.VOC, 'ohm'),
    "humidity": (cp.Sensors.Relative_Humidity, 'percent'),
    "light": (cp.Sensors.Luminance, 'lux'),
    "motion": (cp.Sensors.Motion, 'count'),
    "noise": (cp.Sensors.Ambient_Noise, 'millivolt'),
    "pir": (cp.Sensors.PIR, 'count'),
    "pressure": (cp.Sensors.Pressure, 'hectopascal'),
    "temperature": (cp.Sensors.Temperature, 'degC'),

    "lightenabled": (cp.Diagnostics.Light_Sensor_Enabled, 'boolean'),
    "micenabled": (cp.Diagnostics.Microphone_Sensor_Enabled, 'boolean'),
    "motionenabled": (cp.Diagnostics.Motion_Sensor_Enabled, 'boolean'),
    "rate": (cp.Diagnostics.Report_Interval, 'second'),

    "set_lightenabled": None,
    "set_micenabled": None,
    "set_motionenabled": None,
    "set_rate": None,

    # Sensorbug Service Generated
    "temperature_f": (cp.Sensors.Temperature, 'degF'),
    "noise_avg": None,
    "noise_db": None,

    # GridBallast
    "grid_frequency": (cp.Sensors.Frequency, 'Hz'),
    "heating_status": (cp.Diagnostics.Heating_Status, 'onoff'), # 0 or 1
    "set_point": (cp.Sensors.Water_Heater_Temperature_Set_Point, 'degF'),
    "temp_top": (cp.Sensors.Water_Heater_Temperature_Top, 'degF'),
    "temp_bottom": (cp.Sensors.Water_Heater_Temperature_Bottom, 'degF'),
    "mode": None,

    # OC Gateway
    "alert": (cp.Diagnostics.System_Alert, 'boolean'),
    "alerts": None,
    "altitude": None,
    "coretemp": (cp.Diagnostics.Core_Temperature, 'degC'),
    "disk_free": None,
    "disk_total": (cp.Diagnostics.Storage_Total, 'gigabyte'),
    "disk_used": None,
    "disk_usedpercent": (cp.Diagnostics.Storage_Usage, 'percent'),
    "gpsmapper_status": None,
    "interval": None,
    "latitude": (cp.Sensors.Location_GPS_Latitude, 'degree'),
    "load_15min": None,
    "load_1min": (cp.Diagnostics.CPU_Usage, 'percent'),
    "load_5min": None,
    "longitude": (cp.Sensors.Location_GPS_Longitude, 'degree'),
    "math-evaluate-error": None,
    "mem_available": None,
    "mem_total": (cp.Diagnostics.Memory_Total, 'gigabyte'),
    "mem_used": None,
    "mem_usedpercent": (cp.Diagnostics.Memory_Usage, 'percent'),
    "net_eth0_bytesrecv": (cp.Diagnostics.Network_RX_Count, 'byte'),
    "net_eth0_bytessend": (cp.Diagnostics.Network_TX_Count, 'byte'),
    "net_eth0_dropin": None,
    "net_eth0_dropout": None,
    "net_eth0_errin": None,
    "net_eth0_errout": None,
    "net_eth0_packetsrecv": None,
    "net_eth0_packetssent": None,
    "net_lo_bytesrecv": None,
    "net_lo_bytessend": None,
    "net_lo_dropin": None,
    "net_lo_dropout": None,
    "net_lo_errin": None,
    "net_lo_errout": None,
    "net_lo_packetsrecv": None,
    "net_lo_packetssent": None,
    "net_wlan0_bytesrecv": (cp.Diagnostics.Network_RX_Count, 'byte'),
    "net_wlan0_bytessend": (cp.Diagnostics.Network_TX_Count, 'byte'),
    "net_wlan0_dropin": None,
    "net_wlan0_dropout": None,
    "net_wlan0_errin": None,
    "net_wlan0_errout": None,
    "net_wlan0_packetsrecv": None,
    "net_wlan0_packetssent": None,
    "packets_received": None,
    "packets_received_ok": (cp.Diagnostics.Packet_Count, 'count'),
    "rx_bandwidth": (cp.Sensors.LoRa_Packet_RX_Bandwidth, 'Hz'),
    "rx_crcstatus": None,
    "rx_devaddr": None,
    "rx_frequency": (cp.Sensors.LoRa_Packet_RX_Frequency, 'Hz'),
    "rx_lorasnr": (cp.Sensors.LoRa_Packet_RX_SNR, 'number'),
    "rx_networkid": None,
    "rx_rssi": (cp.Sensors.LoRa_Packet_RX_RSSI, 'number'),
    "rx_spreadingfactor": (cp.Sensors.LoRa_Packet_RX_Spreading_Factor, 'number'),
    "rx_timestamp": (cp.Sensors.LoRa_Packet_RX_Timestamp, 'nanosecond'),
    "trigger": None,
    "tx_bandwidth": (cp.Sensors.LoRa_Packet_TX_Bandwidth, 'Hz'),
    "tx_frequency": (cp.Sensors.LoRa_Packet_TX_Frequency, 'Hz'),
    "tx_power": (cp.Sensors.LoRa_Packet_TX_Power, 'dBm'),
    "tx_spreadingfactor": (cp.Sensors.LoRa_Packet_TX_Spreading_Factor, 'number'),
    "tx_timestamp": (cp.Sensors.LoRa_Packet_TX_Timestamp, 'nanosecond'),
}

def match_sensor_units(topic):
    return topic2sensor.get(topic, None)


class Publisher:
    def __init__(self, id, q):
        self.q = q
        self.poster = cp.ConixPoster(str(get_mac())+"-"+str(id), wave_uri="localhost:4110")

    def process_line(self, line):
        if line == "":
            return
        decoded = json.loads(line)
        if not 'deviceid' in decoded:
            return
        if not 'topic' in decoded:
            return
        if not 'payload' in decoded:
            return
        part_uuid = decoded['deviceid']
        part_topic = decoded['topic']
        part_value = decoded['payload']

        sensor = match_sensor_units(part_topic)
        if sensor is None:
            print('# Skipping {} for deviceid {}'.format(part_topic, part_uuid))
            # addunknowntopic(part_uuid, part_topic)
            return
        sensor_type, sensor_units = sensor

        # Unify booleans to True or False
        if sensor_units == 'boolean' or sensor_units == 'bool':
            part_value = interpret_bool(part_value)
        # Unify onoffs to On or Off
        if sensor_units == 'onoff':
            part_value = interpret_onoff(part_value)

        self.poster.post(part_uuid, sensor_type, part_value, sensor_units)

    def Run(self):
        while True:
            self.process_line(self.q.get())

number_of_threads = 2

def proc(id, q):
    pub = Publisher(id, q)
    pub.Run()

if __name__ == '__main__':
    q = Queue()
    ps = []

    for i in range(number_of_threads):
        ps.append(Process(target=proc, args=(i, q,)))

    for p in ps:
        p.start()

    while True:
            q.put(sys.stdin.readline())