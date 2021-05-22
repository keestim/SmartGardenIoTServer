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
        self.farduino = Serial('/dev/ttyACM1', 9600)

    def getTopicList(self):
        return self.ftopic_list
    
    def getDeviceType(self):
        return self.fdevice_type

    def onMessage(self, topic, payload):
        print(topic + " | " + payload)

        if (("blink_led" in payload) or ("valve_state" in payload)):
            print("writing to arduino")
            print(payload.encode('utf_8'))
            self.farduino.write(payload.encode('utf_8'))
    
        print("")

    def getArdiuno(self):
        return self.farduino

    def readArdinoSerial(self):
        try:
            avaliable_msg = self.farduino.inWaiting()
            return self.farduino.read(avaliable_msg).decode()
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
                        WATERING_SYSTEM_TYPE_NAME, 
                        [DEFAULT_DATA_TOPIC, 
                        CONTROL_DEVICE_TOPIC,
                        SETUP_DEVICE_TOPIC, 
                        WATERING_INFO_TOPIC,
                        "/edge_device/topic_stream"])
    
    mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, DeviceType.edge_device, interface_obj)

    while True:
        msg = interface_obj.readArdinoSerial()

        if len(msg) > 0:
            print(msg)
            mqtt_interface.sendMsg(msg, WATERING_INFO_TOPIC)

        sleep(0.2)
