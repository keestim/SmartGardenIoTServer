from enum import Enum
import threading
from time import sleep
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from DeviceInterface import *

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
        print("run start messaging!")
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

        self.ftopic_list = [("/edge_device/data", 0), 
                            ("/edge_device/setup_device", 0), 
                            ("edge_devices/control_device", 0)]

        self.client = None
        self.fdevice_status = ConnectionStatus.init

        self.fdevice_type = ""

        sleep(1)
        self.__setupReader()

        self.mqtt_connection_initalizer = MQTTConnectInitializer(self)
        self.mqtt_connection_initalizer.start()

    def getDestinationIPAddress(self):
        return self.fdest_ip_address

    def getTopicList(self):
        return self.ftopic_list

    def getDeviceStatus(self):
        return self.fdevice_status

    def __registerDevice(self, topic, payload):
        if self.fdevice_status == ConnectionStatus.attempting_connection:
            if (payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            elif (payload == "initial message received"):
                self.fdevice_status = ConnectionStatus.connected

                if (self.fmqtt_interface is not None):
                    topics_json = json.dumps(self.fmqtt_interface.getTopicList())
                    #store stuff like "topics" and "device_type" as CONSTANTS!"
                    self.sendMsg(
                        str("{\"topics\": ") + str(topics_json) + ", " + 
                            "\"device_type\": \"" + self.fmqtt_interface.getDeviceType() + "\"}", 
                            "/edge_device/setup_device")

    def __encodeTopicsString(self, payload):
        print(payload)
        json_output = json.loads(payload)
        topics = json_output["topics"]

        result_arr = []
        
        for topic in topics:
            result_arr.append((topic, 0))

        return result_arr   

    def __onConnect(self, client, userData, flags, responseCode):
        self.client.subscribe(self.ftopic_list)

    def __assignDeviceInterface(self, payload):
        print("ASSIGNING INTERFACE: " + self.fdest_ip_address)
        json_output = json.loads(payload)
        device_type = json_output["device_type"]

        #maybe use some kind of static enum?
        print("device type: " + str(device_type))
        if (device_type == "PlantMonitor"):
            return PlantMonitorInterface()

    def __onMessage(self, client, userData, msg):
        topic = msg.topic
        payload = msg.payload.decode('ascii')

        print(topic + ", " + str(payload) + "|" + self.fdest_ip_address + "|" + str(self.fdevice_status))

        if self.fdevice_status == ConnectionStatus.connected:
            if (payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            elif (("topics" in payload) and (self.fmqtt_interface is not None)):
                self.ftopic_list = self.__encodeTopicsString(payload)
                self.fmqtt_interface = self.__assignDeviceInterface(payload)
                print(self.fmqtt_interface)


                self.client.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)
            else:
                print(topic + ", " + str(payload) + "|" + self.fdest_ip_address)

                if self.fmqtt_interface is not None:
                    self.fmqtt_interface.onMessage(topic, payload)
        else:
            self.__registerDevice(topic, payload)      
        
    def __setupReader(self):
        print("SETUP READER: " + self.fdest_ip_address)

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
        print("sending msg: " + msgText + " | " + self.fdest_ip_address)
        publish.single(topic, msgText, hostname = self.fdest_ip_address)