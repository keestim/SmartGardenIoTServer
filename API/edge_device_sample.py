from enum import Enum  
import socket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep
import threading

class ConnectionStatus(Enum):
    init = 1
    attempting_connection = 2
    connected = 3

#Source: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
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
    def __init__(self, mqtt_client):
        super().__init__()
        self.fmqtt_client = mqtt_client
        
    def run(self):
        while True:
            if self.fmqtt_client.getDeviceStatus() == ConnectionStatus.init:
                self.fmqtt_client.sendMsg("broadcast", "/edge_device/setup_device")
            elif self.fmqtt_client.getDeviceStatus() == ConnectionStatus.attempting_connection:
                self.fmqtt_client.sendMsg("initial message", "/edge_device/setup_device")
            elif self.fmqtt_client.getDeviceStatus() == ConnectionStatus.connected:
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

        self.__setupReader()

    def __onConnect(self, client, userData, flags, responseCode):
        self.client.subscribe([("/edge_device/data", 0), ("/edge_device/setup_device", 0)])

    def __onMessage(self, client, userData, msg):
        print("New Msg" + str(msg.payload) + msg.topic)
        if self.fdevice_status == ConnectionStatus.attempting_connection:
            if (msg.payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            elif (msg.payload == "initial message received"):
                self.fdevice_status = ConnectionStatus.connected
        elif self.fdevice_status == ConnectionStatus.connected:
            print(msg.topic + ", " + str(msg.payload))

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

global server_ip_address
server_ip_address = "192.168.1.46"

if __name__ == "__main__":
    print(get_ip())
    print(server_ip_address)

    mqtt_interface = BiDirectionalMQTTComms("", get_ip(), server_ip_address)
    mqtt_connection_initalizer = MQTTConnectInitializer(mqtt_interface)
    mqtt_connection_initalizer.start()

    #send message
    mqtt_interface.sendMsg("Hello World")

    #add rest of code, likely in an infinite loop
    #i.e.

    while True:
        #read some sensor/serial data
        mqtt_interface.sendMsg("30 Degrees C")
        sleep(2)
