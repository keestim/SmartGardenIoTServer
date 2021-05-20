from flask import Flask
from flask_cors import CORS

import threading
import pyshark

from time import sleep  
import sys

import repackage
repackage.up()
from SharedClasses.DeviceInterface import * 
from SharedClasses.helper_functions import * 
from SharedClasses.BiDirectionalMQTTComms import * 
from SharedClasses.SystemConstants import *

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
                connection_list.append(BiDirectionalMQTTComms(device_ip_address, ip_data.src, DeviceType.server))

            new_connection_lock.release()

def findDeviceByID(device_id):
    try: 
        int(device_id)
    except ValueError:
        return None
    
    for device in connection_list:
        if device.fmqtt_interface != None:
            if str(device.fmqtt_interface.getDeviceID()) == str(device_id):
                return device

def findDeviceByIDAndType(device_id, device_type):
    potential_device = findDeviceByID(device_id)
    if (type(potential_device.fmqtt_interface) is device_type):
        return potential_device
    else:
        return None

def deviceJSONFormat(device_mqtt_interface):
    output_str = ""
    output_str += "\"id\": " + str(device_mqtt_interface.getDeviceID()) + ", "
    output_str += "\"device_type\" : \"" + device_mqtt_interface.getDeviceType() + "\""

    return "{" + output_str + "}"

def deviceSensorDataJSON(device_mqtt_interface):
    core_output_str = deviceJSONFormat(device_mqtt_interface)
    output_str = core_output_str.replace("{", "").replace("}", "") + ", "

    if (type(device_mqtt_interface) is PlantMonitorInterface):
        output_str += "\"moisture\": " + str(device_mqtt_interface.getMoisture()) + ", "
        output_str += "\"humidity\": " + str(device_mqtt_interface.getHumidity()) + ", "
        output_str += "\"temperature\": " + str(device_mqtt_interface.getTemperature())

    if (type(device_mqtt_interface) is WaterSystemInterface): 
        output_str += "\"pump_state\": \"" + str(device_mqtt_interface.getValveState()) + "\", "
        output_str += "\"total_volume\": " + str(device_mqtt_interface.getWaterVolume())

    return "{" + output_str + "}"

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
#https://restfulapi.net/http-status-codes/

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

#IF NOT RETURNING ANY DATA:
#https://stackoverflow.com/questions/38804385/flask-to-return-nothing-but-only-run-script
#just return a 204 response code

@app.route('/', methods=['GET'])
def home():
    return "Welcome to Smart Garden API"

@app.errorhandler(404)
def page_not_found(e):
    return ("Route Not Found", 404)

#add new route for device information

@app.route("/get_all_devices_info", methods=['GET'])
def get_all_devices_info():
    output_str = ""

    for device in connection_list:
        if output_str != "":
            output_str += ", "

        if device.fmqtt_interface != None:
            output_str += deviceJSONFormat(device.fmqtt_interface)
    
    return "[" + output_str + "]"

@app.route("/get_all_devices_sensor_data", methods=['GET'])
def get_all_devices_sensor_data():
    output_str = ""

    for device in connection_list:
        if output_str != "":
            output_str += ", "

        if device.fmqtt_interface != None:
            output_str += deviceSensorDataJSON(device.fmqtt_interface)
    
    return "[" + output_str + "]"   

@app.route("/get_devices_of_type_info/<device_type_name>", methods=['GET', 'POST'])
def get_devices_of_type_info(device_type_name):
    output_str = ""

    for device in connection_list:
        if output_str != "":
            output_str += ", "

        if device.fmqtt_interface != None:
            if (device.fmqtt_interface.getDeviceType() == device_type_name):
                output_str += deviceJSONFormat(device.fmqtt_interface)
    
    return "[" + output_str + "]"

@app.route("/flash_all_lights", methods=['GET', 'POST'])
def flash_all_lights():
    for device in connection_list:
        if device.fmqtt_interface != None:
            msg_details = getattr(device.fmqtt_interface, 'blinkLED')()
            print(msg_details)
            device.sendMsg(msg_details["payload"], msg_details["topic"])

    return ('', 204)

@app.route("/flash_light/<device_id>", methods=['GET', 'POST'])
def flash_light_for_id(device_id):
    selected_device = findDeviceByID(device_id)

    if selected_device is None:
        return ('No Device Exists for Input ID', 400)
    else:
        msg_details = getattr(selected_device.fmqtt_interface, 'blinkLED')()
        selected_device.sendMsg(msg_details["payload"], msg_details["topic"])

    return ('', 204)

@app.route("/change_valve_state/<device_id>/<state>", methods=['GET', 'POST'])
def turn_on_valve(device_id, state):
    selected_device = None

    if (not device_id.is_integer()):
        return ('', 400)

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

    return ('', 204)

#better to spawn a therad for this
#test this out!
@app.route("/water_set_volume/<device_id>/<volume>", methods=['GET', 'POST'])
def water_set_volume(device_id, volume):
    selected_device = None

    #validate that id is an interger

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
            print("Volume: " + str(device.fmqtt_interface.getWaterVolume()))
            continue

        msg_details = getattr(selected_device.fmqtt_interface, 'closeValve')()
        device.sendMsg(msg_details["payload"], msg_details["topic"])

    return ('', 204)

#something about avaliable methods?

#probably swap to GET variables approach
#this makes for a most readable URL
#maybe something to add to note either client or server side
#implement clean exit for script!
@app.route("/water_plant_to_target_moisture/<plant_id>/<watering_id>/<target_moisture>", methods=['GET', 'POST'])
def water_plant_to_target_moisture():
    return "Watering plant"

#SCRIPT ENTRY POINT
if __name__ == "__main__":
    try:
        server_network_interface = sys.argv[1]
    except:
        print("You must enter the network interface that you're connected through")
        exit()

    mqtt_sniffer = MQTTSniffer(server_network_interface)
    mqtt_sniffer.start()
    app.run()