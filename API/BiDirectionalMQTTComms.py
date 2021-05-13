from enum import Enum
import threading
from time import sleep
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json

class ConnectionStatus(Enum):
    init = 1
    attempting_connection = 2
    connected = 3
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
    def __init__(self, device_ip_address, dest_ip_address, mqtt_interface = None, port = 1883, keepAlive = 60):
        self.fdest_ip_address = dest_ip_address
        self.fdevice_ip_address = device_ip_address

        self.fmqtt_interface = mqtt_interface

        self.fport = port
        self.fkeepAlive = keepAlive

        self.fmqtt_subscriber_thread = None

        self.client = None
        self.fdevice_status = ConnectionStatus.init
        sleep(2)
        self.__setupReader()

        self.sendMsg("test msg")
        #add field for device topics

    def __registerDevice(self, topic, payload):
        if self.fdevice_status == ConnectionStatus.attempting_connection:
            if (payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            elif (payload == "initial message received"):
                self.fdevice_status = ConnectionStatus.connected

                if (self.fmqtt_interface is not None):
                    topics_json = json.dumps(self.fmqtt_interface.getTopicList()
                    self.sendMsg(str("{'topics': ") + str(topics_json) + "}"), "/edge_device/setup_device")

    def __encodeTopicsString(self, payload):
        topics = json.loads(payload["topics"])
        result_arr = []
        
        for topic in topics:
            result_arr.append((topic, 0))

        return result_arr   

    def __onConnect(self, client, userData, flags, responseCode):
        #default topics!
        self.client.subscribe([("/edge_device/data", 0), ("/edge_device/setup_device", 0)])

    def __onMessage(self, client, userData, msg):
        topic = msg.topic
        payload = msg.payload.decode('ascii')

        self.__registerDevice(topic, payload)                
        if self.fdevice_status == ConnectionStatus.connected:
            #incase miscommunication occurs
            #find a better way to handle this!
            #seems to only occur for server!
            if (payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            else:
                print(topic + ", " + str(payload))

            #need detect and decode topic msg!
        
    def __setupReader(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.__onConnect
        self.client.on_message = self.__onMessage

        self.client.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)

        self.fmqtt_subscriber_thread = MQTTSubscriberThread(self.client)
        self.fmqtt_subscriber_thread.start()

        self.sendMsg("broadcast", "/edge_device/setup_device")
        self.fdevice_status = ConnectionStatus.attempting_connection

        self.sendMsg("initial message", "/edge_device/setup_device")

    def getDeviceStatus(self):
        return self.fdevice_status

    def sendMsg(self, msgText, topic = "/edge_device/data"):
        publish.single(topic, msgText, hostname=self.fdest_ip_address)

        