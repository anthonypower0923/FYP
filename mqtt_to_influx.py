#!/usr/bin/env python3

"""
Skeleton of script taken from
https://gist.github.com/zufardhiyaulhaq/fe322f61b3012114379235341b935539
"""

"""A MQTT to InfluxDB Bridge

This script receives MQTT data and saves those to InfluxDB.

"""

import re
from typing import NamedTuple
import os

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '87.44.27.48'
INFLUXDB_USER = 'influx'
INFLUXDB_PASSWORD = os.environ['INFLUX_TOKEN']
INFLUXDB_DATABASE = 'bandwidth'

MQTT_ADDRESS = '87.44.27.48'
MQTT_USER = 'iotuser'
MQTT_PASSWORD = 'iotpassword'
MQTT_TOPIC = 'bandwidth/+/+'  # [room]/[temperature|humidity|light|status]
MQTT_REGEX = 'bandwidth/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


class NetworkData(NamedTuple):
    location: str
    measurement: str
    value: float


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    network_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    if network_data is not None:
        _send_sensor_data_to_influxdb(network_data)


def _parse_mqtt_message(topic, payload):
    match = re.match(MQTT_REGEX, topic)
    if match:
        location = match.group(1)
        measurement = match.group(2)
        if measurement == 'status':
            return None
        return NetworkData(location, measurement, float(payload))
    else:
        return None


def _send_sensor_data_to_influxdb(network_data):
    json_body = [
        {
            'measurement': network_data.measurement,
            'tags': {
                'location': network_data.location
            },
            'fields': {
                'value': network_data.value
            }
        }
    ]
    print (json_body)
    influxdb_client.write_points(json_body)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main():
    _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    # mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()