from flask import Flask, request, jsonify
import threading
import pyshark
from time import sleep  
from helper_functions import *
import sys
from BiDirectionalMQTTComms import * 

global add_new_connection_lock
global mqtt_ip_addresses
global connection_list

connection_list = []
mqtt_ip_addresses = []
add_new_connection_lock = threading.Lock()
device_ip_address = get_ip()

class AddMQTTConnection(threading.Thread):
    def __init__(self, packet_item):
        super().__init__()
        self.fpacket_item = packet_item

    def run(self):
        while True:
            try:
                add_new_connection_lock.acquire()
            except:
                sleep(0.5)
                continue
            finally:
                try:
                    ip_data = self.fpacket_item.ip
                    mqtt_data = self.fpacket_item.mqtt
                except:
                    add_new_connection_lock.release()
                    return
            
                if (ip_data.src not in mqtt_ip_addresses) and not(ip_data.src == device_ip_address):
                    mqtt_ip_addresses.append(ip_data.src)

                    print(mqtt_data)                    
                    connection_list.append(BiDirectionalMQTTComms(device_ip_address, ip_data.src))

                add_new_connection_lock.release()
                return

class MQTTSniffer(threading.Thread):
    def __init__(self, interfacename):
        super().__init__()
        self.fcapture = pyshark.LiveCapture(interface = interfacename)

    def run(self):
        for item in self.fcapture.sniff_continuously():
            add_connection_thread = AddMQTTConnection(item)
            add_connection_thread.start()

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "API Test"

@app.route("/probe_devices", methods=['GET'])
def probe_devices():
    devices_str = ""

    for device in connection_list:
        devices_str = devices_str + device.fdest_ip_address + ", "
        device.sendMsg("The bois")

    return devices_str

@app.route("/flash_all_lights", methods=['GET'])
def flash_all_lights():
    for device in connection_list:
        if device.fmqtt_interface != None:
            msg_details = getattr(device.fmqtt_interface, 'blinkLED')()
            print(msg_details)
            device.sendMsg(msg_details["payload"], msg_details["topic"])

    return "Flash LIGHTS!"

@app.route("/get_device_details", methods=['GET'])
def get_device_details():
    output_str = ""

    for device in connection_list:
        if device.fmqtt_interface != None:
            device_interface = device.fmqtt_interface
            output_str = output_str + device_interface.fDeviceType + "," + str(device_interface.ftype_id) + "<br/>"
    
    return output_str


#something about avaliable methods?

if __name__ == "__main__":
    try:
        server_network_interface = sys.argv[1]
    except:
        print("You must enter the network interface that you're connected through")
        exit()

    mqtt_sniffer = MQTTSniffer(server_network_interface)
    mqtt_sniffer.start()
    app.run()

#maybe something to add to note either client or server side