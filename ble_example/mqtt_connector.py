import socket
import os
import argparse
import paho.mqtt.client as paho
from paho import mqtt
import time

SOCKET_HOST = os.getenv('SOCKET_HOST', 'localhost')
SOCKET_PORT = int(os.getenv('SOCKET_PORT', '9999'))
BUFFER_SIZE = 4

MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST')
MQTT_BROKER_PORT = os.getenv('MQTT_BROKER_PORT')
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC = os.getenv('MQTT_TOPIC')
MQTT_TLS = os.getenv('MQTT_TLS')


class DeviceSerial():
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect((host, port))
                return
            except:
                time.sleep(1)

    def read(self):
        buf = bytearray()
        buf.extend(self.sock.recv(4))
        return buf
    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def main():
    parser = argparse.ArgumentParser(prog='MQTT Connector', description='')
    parser.add_argument('--host', default=SOCKET_HOST)
    parser.add_argument('--port', default=SOCKET_PORT, type=int)
    parser.add_argument('--broker-host', default=MQTT_BROKER_HOST)
    parser.add_argument('--broker-port', default=MQTT_BROKER_PORT, type=int)
    parser.add_argument('--username', default=MQTT_USERNAME)
    parser.add_argument('--password', default=MQTT_PASSWORD)
    parser.add_argument('--topic', default=MQTT_TOPIC)
    parser.add_argument('--tls', default=MQTT_TLS, action='store_true')
    
    args = parser.parse_args()
    print(args)

    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect
    if args.tls:
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.on_connect = on_connect

    client.username_pw_set(args.username, args.password)
    client.connect(args.broker_host, args.broker_port)

    device = DeviceSerial(args.host, args.port)
    while True:
        b = device.read()
        if len(b) == 4:
            value = int.from_bytes(b, byteorder='little')
            print(value)
            try:
                client.publish(args.topic, '{ "data": ' + str(value) + '}')
            except Exception as e:
                print(e)
                pass 

if __name__ == '__main__':
    main()