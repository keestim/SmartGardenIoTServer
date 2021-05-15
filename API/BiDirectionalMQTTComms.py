from enum import Enum
import threading
from time import sleep
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from DeviceInterface import *
from colorama import Fore, Back, Style

class ConnectionStatus(Enum):
    init = 1
    attempting_connection = 2
    connection_accepted = 3
    device_registered = 4

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
            try:
                self.fmqtt_bi_comms.fconnection_setup_lock.acquire()
            finally:
                if self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.init:
                    self.fmqtt_bi_comms.fdevice_status = ConnectionStatus.attempting_connection
                    self.fmqtt_bi_comms.sendMsg("broadcast", "/edge_device/setup_device")
                elif self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.attempting_connection:
                    self.fmqtt_bi_comms.sendMsg("initial message", "/edge_device/setup_device")
                else:
                    self.fmqtt_bi_comms.fconnection_setup_lock.release()
                    exit()

                self.fmqtt_bi_comms.fconnection_setup_lock.release()
                sleep(1)

class RegisterDeviceThread(threading.Thread):
    def __init__(self, MQTT_comms, topic, payload):
        super().__init__()
        self.fMQTT_comms = MQTT_comms
        self.ftopic = topic
        self.fpayload = payload

    def run(self):
        if self.fMQTT_comms.getDeviceStatus == ConnectionStatus.attempting_connection:
            if (self.fpayload == "initial message"):
                self.fMQTT_comms.sendMsg("initial message received", "/edge_device/setup_device")
            elif (self.fpayload == "initial message received"):
                #just incase, remove this!
                self.fMQTT_comms.sendMsg("initial message received", "/edge_device/setup_device")
                self.fMQTT_comms.setDeviceStatus(ConnectionStatus.connection_accepted)
                return
        elif (self.fMQTT_comms.fdevice_status == ConnectionStatus.connection_accepted):
            if (self.fMQTT_comms.fmqtt_interface is not None):
                sleep(7)

                #wait for other side of connection to finish
                topics_json = json.dumps(self.fMQTT_comms.fmqtt_interface.getTopicList())
                #store stuff like "topics" and "device_type" as CONSTANTS!"
                self.fMQTT_comms.sendMsg(
                    str("{\"topics\": ") + str(topics_json) + ", " + 
                        "\"device_type\": \"" + self.fMQTT_comms.fmqtt_interface.getDeviceType() + "\"}", 
                        "/edge_device/setup_device")
            
            #probably would be good to have some kind of response, etc for this 
            self.fMQTT_comms.setDeviceStatus(ConnectionStatus.device_registered)
            return  

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

        self.__setupReader()

        self.fconnection_setup_lock = threading.Lock()

        self.mqtt_connection_initalizer = MQTTConnectInitializer(self)
        self.mqtt_connection_initalizer.start()

        #create a set, so that this can be set through MQTTConnectInitializer
        
    def getDestinationIPAddress(self):
        return self.fdest_ip_address

    def getTopicList(self):
        return self.ftopic_list

    def getDeviceStatus(self):
        return self.fdevice_status

    def __encodeTopicsString(self, payload):
        print(Fore.RED + payload)
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

        if (self.fdevice_status == ConnectionStatus.device_registered):
            if (payload == "initial message"):
                self.sendMsg("initial message received", "/edge_device/setup_device")
            elif ("topics" in payload):
                self.ftopic_list = self.__encodeTopicsString(payload)
                self.fmqtt_interface = self.__assignDeviceInterface(payload)
                print(self.fmqtt_interface)

                self.client.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)
            else:
                if self.fmqtt_interface is not None:
                    self.fmqtt_interface.onMessage(topic, payload)
        else:
            registration_thread = RegisterDeviceThread(self, topic, payload)
            registration_thread.start()
        
    def __setupReader(self):
        print("setup reader for: " + self.fdest_ip_address + "|" + self.fdevice_ip_address)
        self.client = mqtt.Client()
        self.client.on_connect = self.__onConnect
        self.client.on_message = self.__onMessage

        self.client.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)

        self.fmqtt_subscriber_thread = MQTTSubscriberThread(self.client)
        self.fmqtt_subscriber_thread.start()

    def getDeviceStatus(self):
        return self.fdevice_status

    def setDeviceStatus(self, new_status):
        self.fdevice_status = new_status

    def sendMsg(self, msgText, topic = "/edge_device/data"):
        print(Fore.YELLOW + "sending msg: " + msgText + " | " + self.fdest_ip_address)
        publish.single(topic, msgText, hostname = self.fdest_ip_address)