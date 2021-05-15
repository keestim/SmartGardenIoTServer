from enum import Enum  
import socket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep
import threading
import sys
from helper_functions import *

from BiDirectionalMQTTComms import * 

class CommunicationInterface():
    def __init__(self, device_type, topics):
        self.ftopic_list = topics
        self.fdevice_type = device_type

    def getTopicList(self):
        return self.ftopic_list
    
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

    interface_obj = CommunicationInterface("plant_reader", ["/edge_device/data", "/edge_device/setup_device", "/edge_device/topic_stream"])
    mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, interface_obj)