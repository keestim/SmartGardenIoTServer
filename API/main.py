from flask import Flask, request, jsonify
import threading
import pyshark
from time import sleep  
import sys

import repackage
repackage.up()
from SharedClasses.DeviceInterface import * 
from SharedClasses.helper_functions import * 
from SharedClasses.BiDirectionalMQTTComms import * 

connection_list = []
mqtt_ip_addresses = []
device_ip_address = get_ip()
new_connection_lock = threading.Lock()

class MQTTSniffer(threading.Thread):
    def __init__(self, interfacename):
        global new_connection_lock
        super().__init__()
        self.fcapture = pyshark.LiveCapture(interface = interfacename)

    def run(self):
        for item in self.fcapture.sniff_continuously():
            try:
                new_connection_lock.acquire()
            except:
                continue

            try:
                ip_data = item.ip
                mqtt_data = item.mqtt
            except:
                new_connection_lock.release()
                continue
                            
            if (ip_data.src not in mqtt_ip_addresses) and not(ip_data.src == device_ip_address):
                mqtt_ip_addresses.append(ip_data.src)

                print(mqtt_data)
                print("Setting up MQTT Connection with IP: " + ip_data.src)
                
                connection_list.append(BiDirectionalMQTTComms(device_ip_address, ip_data.src, DeviceType.server))

            new_connection_lock.release()

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "API Test"


@app.route("/get_device_details", methods=['GET'])
def get_device_details():
    output_str = ""

    for device in connection_list:
        if output_str == "":
            output_str += "{"
        else:
            output_str += ", "

        if device.fmqtt_interface != None:
            device_interface = device.fmqtt_interface
            output_str += "["
            output_str += "[\"id\": " + int(device_interface.getDeviceID()) + ", "
            output_str += "\"device_type\" : \"" + device_interface.getDeviceType() + "\""
            output_str += "]"
        
    return output_str + "}"

@app.route("/get_device_of_type/<type>", methods=['GET'])
def get_device_of_type(type):
    output_str = ""

    for device in connection_list:
        if output_str == "":
            output_str += "{"
        else:
            output_str += ", "

        if device.fmqtt_interface != None:
            if (device.fmqtt_interface.getDeviceType() == type):
                device_interface = device.fmqtt_interface
                output_str += "["
                output_str += "\"id\": " + int(device_interface.getDeviceID()) + ", " 
                output_str += "\"device_type\" : \"" + device_interface.getDeviceType() + "\""
                output_str += "]"
    return output_str + "}"

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

@app.route("/change_valve_state/<device_id>/<state>", methods=['GET'])
def turn_on_valve(device_id, state):
    selected_device = None

    #validate that id is an in

    if state not in ["open", "closed"]:
        return "invalid state provided"

    for device in connection_list:
        if device.fmqtt_interface != None:
            print(device.fmqtt_interface)
            if (type(device.fmqtt_interface) is WaterSystemInterface):
                if (str(device.fmqtt_interface.getDeviceID()) == str(device_id)):
                    selected_device = device
                    break
    
    if selected_device is not None:
        if state == "open":
            msg_details = getattr(selected_device.fmqtt_interface, 'openValve')()
        elif state == "closed":
            msg_details = getattr(selected_device.fmqtt_interface, 'closeValve')()
        
        print(msg_details)
        device.sendMsg(msg_details["payload"], msg_details["topic"])
        
    return "Pump " + state

#better to spawn a therad for this
@app.route("/water_set_volume/<device_id>/<volume>", methods=['GET'])
def water_set_volume(device_id, volume):
    selected_device = None

    #validate that id is an in

    for device in connection_list:
        if device.fmqtt_interface != None:
            print(device.fmqtt_interface)
            if (type(device.fmqtt_interface) is WaterSystemInterface):
                if (str(device.fmqtt_interface.getDeviceID()) == str(device_id)):
                    #make sure this is by reference!
                    selected_device = device
                    break
    
    if selected_device is not None:
        msg_details = getattr(selected_device.fmqtt_interface, 'openValve')()
        print(msg_details)
        device.sendMsg(msg_details["payload"], msg_details["topic"])

        while (device.fmqtt_interface.getWaterVolume() <= float(volume)):
            sleep(0.2)
            continue

        msg_details = getattr(selected_device.fmqtt_interface, 'closeValve')()
        device.sendMsg(msg_details["payload"], msg_details["topic"])

    return "Specified Volume Released"

#something about avaliable methods?

#probably swap to GET variables approach
#this makes for a most readable URL
@app.route("/water_plant_to_target_moisture/<plant_id>/<watering_id>/<target_moisture>")
def water_plant_to_target_moisture():
    return "Watering plant"

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
#implement clean exit for script!