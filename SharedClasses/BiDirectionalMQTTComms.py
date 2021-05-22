from enum import Enum
import threading
from time import sleep
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import sys
import repackage
import subprocess
repackage.up()
from SharedClasses.DeviceInterface import PlantMonitorInterface, SMOKE_MONITOR_TYPE_NAME, SmokeSensorInterface, WaterSystemInterface, PLANT_MONITOR_TYPE_NAME, WATERING_SYSTEM_TYPE_NAME, PAYLOAD_MSG_KEY, TOPIC_MSG_KEY
from SharedClasses.helper_functions import * 
from SharedClasses.SystemConstants import *

BROADCAST_MSG_TXT = "broadcast"
INIT_MSG_TXT = "initial message"
INIT_RECEIVED_MSG_TXT = "initial message received"

class ConnectionStatus(Enum):
    init = 1
    attempting_connection = 2
    connected = 3

class DeviceType(Enum):
    server = 1
    edge_device = 2

class MQTTSubscriberThread(threading.Thread):
    def __init__(self, mqtt_connection):
        super().__init__()
        self.fmqtt_connection = mqtt_connection
        print("new sub thread!")
        self.fKillLoop = False

    def setKillLoop(self, input_value):
        self.fKillLoop = input_value

    def run(self):
        while True and self.fKillLoop is False:
            try:
                self.fmqtt_connection.getClient().loop(0.01) #check for messages
                sleep(0.1)
            except:
                continue

        exit()

#TODO: potentially add a new enum to enforce that "initial message received" is sent before enum!
#http://www.steves-internet-guide.com/multiple-client-connections-python-mqtt/

class MQTTConnectInitializer(threading.Thread):
    def __init__(self, mqtt_bi_comms):
        super().__init__()
        self.fmqtt_bi_comms = mqtt_bi_comms
        
    def run(self):
        while True:
            if self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.init:
                self.fmqtt_bi_comms.sendMsg(BROADCAST_MSG_TXT, SETUP_DEVICE_TOPIC)
            elif self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.attempting_connection:
                self.fmqtt_bi_comms.sendMsg(INIT_MSG_TXT, SETUP_DEVICE_TOPIC)
            elif self.fmqtt_bi_comms.getDeviceStatus() == ConnectionStatus.connected:
                exit()

            sleep(1)

class CoupledPlantMoistureWatcher(threading.Thread):
    def __init__(self, mqtt_bi_comms):
        super().__init__()
        self.fmqtt_bi_comms = mqtt_bi_comms

    def waterPlantToSetLevel(self):
        mqtt_interface_obj = self.fmqtt_bi_comms.getInterfaceObj()

        msg_details = getattr(mqtt_interface_obj, 'openValve')()
        self.fmqtt_bi_comms.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

        while (mqtt_interface_obj.getCoupledPlantInterface().getMoisturePercentage() <= mqtt_interface_obj.getTriggerMoistureLevel()):
            sleep(0.5)
            continue

        msg_details = getattr(mqtt_interface_obj, 'closeValve')()
        self.fmqtt_bi_comms.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

    def run(self):
        while True:
            mqtt_interface_obj = self.fmqtt_bi_comms.getInterfaceObj()

            if (mqtt_interface_obj.getCoupledPlantInterface().getMoisturePercentage() <= mqtt_interface_obj.getTriggerMoistureLevel()):
                self.waterPlantToSetLevel()

            sleep(0.5)

class BiDirectionalMQTTComms():
    def __init__(self, device_ip_address, dest_ip_address, device_type, mqtt_interface = None, port = 1883, keepAlive = 60):
        self.fdest_ip_address = dest_ip_address
        self.fdevice_ip_address = device_ip_address

        self.fmqtt_interface = mqtt_interface

        self.fport = port
        self.fkeepAlive = keepAlive

        self.fmqtt_subscriber_thread = None

        self.fdevice_type = device_type

        #Construct a list of topics that all devices use
        self.ftopic_list = [(DEFAULT_DATA_TOPIC, 0), 
                            (SETUP_DEVICE_TOPIC, 0), 
                            (CONTROL_DEVICE_TOPIC, 0)]

        self.fclient = None
        self.fdevice_status = ConnectionStatus.init
        self.__setupReader()

        self.mqtt_connection_initalizer = MQTTConnectInitializer(self)
        self.mqtt_connection_initalizer.start()
        self.fdevice_status = ConnectionStatus.attempting_connection

        self.fmoisture_watcher_thread = None

        self.fThingsBoardKey = ""

    def getInterfaceObj(self):
        return self.fmqtt_interface

    def getMoistureWatcherThread(self):
        return self.fmoisture_watcher_thread

    def setMoistureWatcherThread(self, input_thread):
        if (self.fmoisture_watcher_thread is not None):
            self.fmoisture_watcher_thread.join()

            msg_details = getattr(self.fmqtt_interface, 'closeValve')()
            self.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

        self.fmoisture_watcher_thread = input_thread

    def getDestinationIPAddress(self):
        return self.fdest_ip_address

    def getTopicList(self):
        return self.ftopic_list

    def getDeviceStatus(self):
        return self.fdevice_status

    def __registerDevice(self, topic, payload):
        if self.fdevice_status == ConnectionStatus.attempting_connection:
            if (payload == INIT_MSG_TXT):
                self.sendMsg(INIT_RECEIVED_MSG_TXT, SETUP_DEVICE_TOPIC)
            elif (payload == INIT_RECEIVED_MSG_TXT):
                self.fdevice_status = ConnectionStatus.connected

                #TODO: need to do this more elegantly!
                self.sendMsg(INIT_RECEIVED_MSG_TXT, SETUP_DEVICE_TOPIC)

                if (self.fmqtt_interface is not None):
                    topics_json = json.dumps(self.fmqtt_interface.getTopicList())

                    self.sendMsg(
                        "{\"topics\": " + str(topics_json) + ", " + 
                        "\"device_type\": \"" + str(self.fmqtt_interface.getDeviceType()) + "\"}", 
                        SETUP_DEVICE_TOPIC)

    def __encodeTopicsString(self, payload):
        json_output = json.loads(payload)
        topics = json_output["topics"]

        result_arr = []
        
        for topic in topics:
            result_arr.append((topic, 0))

        return result_arr   

    def __setupReader(self):
        self.fclient = mqtt.Client()
        self.fclient.on_connect = self.__onConnect
        self.fclient.on_message = self.__onMessage

        self.fclient.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)

        self.fmqtt_subscriber_thread = MQTTSubscriberThread(self)
        self.fmqtt_subscriber_thread.start()

    def __onConnect(self, client, userData, flags, responseCode):
        self.fclient.subscribe(self.ftopic_list)

    def __assignDeviceInterface(self, payload):
        if self.fmqtt_interface is None:
            json_output = json.loads(payload)
            device_type = json_output['device_type']

            print("DEVICE TYPE")
            print(device_type)

            if (device_type == PLANT_MONITOR_TYPE_NAME):
                self.fmqtt_interface = PlantMonitorInterface()
            elif (device_type == WATERING_SYSTEM_TYPE_NAME):
                self.fmqtt_interface = WaterSystemInterface()
            elif (device_type == SMOKE_MONITOR_TYPE_NAME):
                self.fmqtt_interface = SmokeSensorInterface()

    def __onMessage(self, client, userData, msg):
        sleep(0.1)

        topic = msg.topic
        payload = msg.payload.decode('ascii')

        if self.fdevice_status == ConnectionStatus.connected:
            if (payload == INIT_MSG_TXT):
                self.sendMsg(INIT_RECEIVED_MSG_TXT, SETUP_DEVICE_TOPIC)
            elif ("topics" in payload):
                print("TOPICS MSG RECEIVED!")
                print("Status:")
                print(self.fdevice_status)

                self.ftopic_list = self.__encodeTopicsString(payload)
                self.fclient.subscribe(self.ftopic_list)
                
                self.__assignDeviceInterface(payload)
                
                self.fmqtt_subscriber_thread.setKillLoop(True)

                #self.fclient.disconnect()
                #sleep(0.5)

                self.fclient.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)
                
                self.fmqtt_subscriber_thread = MQTTSubscriberThread(self)
                self.fmqtt_subscriber_thread.start()
                
                sleep(1)

                if (self.fdevice_type is DeviceType.server):
                    if self.fmqtt_interface is not None:
                        print("output to thingsboard!")
                        print("{\"unique_thingsboard_id\": \"" + str(self.fmqtt_interface.getUniqueThingsBoardID()) + "\"}")

                        self.sendMsg("{\"unique_thingsboard_id\": \"" + str(self.fmqtt_interface.getUniqueThingsBoardID()) + "\"}")
            elif ("unique_thingsboard_id" in payload):
                print(topic + " | " + payload)

                try:
                    device_data = json.loads(payload)
                except:
                    print("json error")
                    return

                print(device_data["unique_thingsboard_id"])
                                
                self.fThingsBoardKey = device_data["unique_thingsboard_id"]
            else:
                if self.fmqtt_interface is not None:
                    self.fmqtt_interface.onMessage(topic, payload)
                    
        else:
            self.__registerDevice(topic, payload)      

    def __onPublish(client, userdata, mid):
        sleep(0.5)
        
    def getDeviceStatus(self):
        return self.fdevice_status

    def getClient(self):
        return self.fclient

    def sendMsg(self, msgText, topic = DEFAULT_DATA_TOPIC):
        publish.single(topic, msgText, hostname = self.fdest_ip_address)
        print("Sending MSG: " + msgText)

        if (self.fdevice_type == DeviceType.edge_device):
            if (self.fThingsBoardKey != ""):
                command = 'curl -v -X POST -d "' + msgText + '" https://demo.thingsboard.io/api/v1/' + self.fThingsBoardKey + '/telemetry --header "Content-Type:application/json"'
                print(str(command))
                subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
