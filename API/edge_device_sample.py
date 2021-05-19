from enum import Enum  
import socket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep
import threading
import sys
import repackage
repackage.up()
from SharedClasses.BiDirectionalMQTTComms import * 
from SharedClasses.DeviceInterface import * 
from SharedClasses.helper_functions import * 

class CommunicationInterface():
    def __init__(self, device_type, topics):
        self.ftopic_list = topics
        self.fdevice_type = device_type

    def getTopicList(self):
        return self.ftopic_list
    
    def getDeviceType(self):
        return self.fdevice_type

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)

global server_ip_address

if __name__ == "__main__":
    try:
        server_ip_address = sys.argv[1]
    except:
        print("You must enter the server ip address as an additional command line arg")
        exit()

    print(get_ip())
    print(server_ip_address)

    #try make this constant!
    interface_obj = CommunicationInterface(
                        "PlantMonitor", 
                        [DEFAULT_DATA_TOPIC, 
                        CONTROL_DEVICE_TOPIC, 
                        SETUP_DEVICE_TOPIC, 
                        "/edge_device/topic_stream"])
    
    mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, interface_obj)
