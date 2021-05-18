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
from serial import Serial as Serial

class CommunicationInterface():
    def __init__(self, device_type, topics):
        self.ftopic_list = topics
        self.fdevice_type = device_type
        self.farduino = Serial('/dev/ttyACM0', 9600)

    def getTopicList(self):
        return self.ftopic_list
    
    def getDeviceType(self):
        return self.fdevice_type

    def onMessage(self, topic, payload):
        if ("blink_led" in payload):
            self.farduino.write(payload.encode('utf_8'))
        
        if ("valve_state" in payload):
            #fix this, try to pass payload straight in!
            self.farduino.write(payload.encode('utf_8'))

        print("")

    def getArdiuno(self):
        return self.farduino

    def readArdinoSerial(self):
        try:
            return self.farduino.read(self.farduino.inWaiting()).decode() 
        except:
            return ""

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
                        "WateringSystem", 
                        ["/edge_device/data", 
                        "/edge_device/water_info"
                        "/edge_device/control_device", 
                        "/edge_device/setup_device", 
                        "/edge_device/topic_stream"])
    
    mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, DeviceType.edge_device, interface_obj)

    while True:
        msg = interface_obj.readArdinoSerial()

        if len(msg) > 0:
            print(msg)
            mqtt_interface.sendMsg(msg, "/edge_device/water_info")
            print("_______________________")

        sleep(0.2)
