from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import pyshark
import socket
from enum import Enum
from time import sleep  

class ConnectionStatus(Enum):
    init = 1
    attempting_connection = 2
    connected = 3

class MQTTSniffer(threading.Thread):
    def __init__(self, connection_list):
        super().__init__()
        self.fmqtt_ip_addresses = []
        self.fdevice_ip_address = self.get_ip()
        self.fcapture = pyshark.LiveCapture(interface='enp0s25')
        self.fconnection_list = connection_list

    def run(self):
        for item in self.fcapture.sniff_continuously():
            try:
                mqtt_data = item.mqtt
                ip_data = item.ip

                if (ip_data.src not in self.fmqtt_ip_addresses) and not(ip_data.src == self.fdevice_ip_address):
                    self.fmqtt_ip_addresses.append(ip_data.src)

                    print(mqtt_data)
                    print("New IP: " + ip_data.src)
                    
                    print("New Connection")
                    new_mqtt_connection = BiDirectionalMQTTComms("Test", self.fdevice_ip_address, ip_data.src)
                    
                    mqtt_connection_initalizer = MQTTConnectInitializer(new_mqtt_connection)
                    mqtt_connection_initalizer.start()

                    self.fconnection_list.append(new_mqtt_connection)

                    print(len(self.fconnection_list))

            except:
                continue

    #Source: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

class MQTTSubscriberThread(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        self.fmqtt_client = mqtt_client
        
    def run(self):
        self.fmqtt_client.loop_forever()

class MQTTConnectInitializer(threading.Thread):
    def __init__(self, mqtt_bi_comms):
        super().__init__()
        self.fmqtt_bi_comms = mqtt_bi_comms
        
    def run(self):
        while True:
            if self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.init:
                self.fmqtt_bi_comms.sendMsg("broadcast", "/edge_device/setup_device")
            elif self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.attempting_connection:
                self.fmqtt_bi_comms.sendMsg("initial message", "/edge_device/setup_device")
            elif self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.connected:
                exit()

            sleep(1)

class BiDirectionalMQTTComms:
    def __init__(self, topic, device_ip_address, dest_ip_address, port = 1883, keepAlive = 60):
        self.fdest_ip_address = dest_ip_address
        self.fdevice_ip_address = device_ip_address

        self.ftopic = topic

        self.fport = port
        self.fkeepAlive = keepAlive

        self.fmqtt_subscriber_thread = None

        self.client = None
        self.fdevice_status = ConnectionStatus.init
        sleep(2)
        self.__setupReader()

        self.sendMsg("test msg")
        #add field for device topics
        
    def __onConnect(self, client, userData, flags, responseCode):
        self.client.subscribe([("/edge_device/data", 0), ("/edge_device/setup_device", 0)])

    def __onMessage(self, client, userData, msg):
        topic = str(msg.topic).encode("utf-8")
        payload = str(msg.payload).encode("utf-8")

        print("New Msg" + payload + " | " + topic)

        if self.fdevice_status == ConnectionStatus.attempting_connection:
            if (payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            elif (payload == "initial message received"):
                self.fdevice_status = ConnectionStatus.connected
        elif self.fdevice_status == ConnectionStatus.connected:
            print(topic + ", " + str(payload))

        
    def __setupReader(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.__onConnect
        self.client.on_message = self.__onMessage

        self.client.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)

        self.fmqtt_subscriber_thread = MQTTSubscriberThread(self.client)
        self.fmqtt_subscriber_thread.start()

        print("broadcast msg!")
        self.sendMsg("broadcast", "/edge_device/setup_device")
        self.fdevice_status = ConnectionStatus.attempting_connection

        print("init msg")
        self.sendMsg("initial message", "/edge_device/setup_device")

    def getDeviceStatus(self):
        return self.fdevice_status

    def sendMsg(self, msgText, topic = "/edge_device/data"):
        print("Sending Msg: " + topic + " | " + self.fdest_ip_address + "|" + msgText)
        publish.single(topic, msgText, hostname=self.fdest_ip_address)

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "API Test"

if __name__ == "__main__":
    active_mqtt_connections = []
    mqtt_sniffer = MQTTSniffer(active_mqtt_connections)
    mqtt_sniffer.start()
    app.run()
