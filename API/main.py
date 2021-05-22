from flask import Flask, request
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

#contains is a thread that runs a packet sniffer, investigating any incoming packets
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

            #if the packet doesn't contain IP and MQTT layers, an exception will be thrown
            try:
                ip_data = item.ip
                mqtt_data = item.mqtt
            except:
                new_connection_lock.release()
                continue
                            
            if (ip_data.src not in mqtt_ip_addresses) and not(ip_data.src == device_ip_address):
                mqtt_ip_addresses.append(ip_data.src)
                new_mqtt_connection = BiDirectionalMQTTComms(device_ip_address, ip_data.src, DeviceType.server)
                connection_list.append(new_mqtt_connection)

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

def findDevicesByType(device_type):
    devices_of_type = []

    for device in connection_list:
        if device.fmqtt_interface != None:
            if (type(device.fmqtt_interface) is device_type):
                devices_of_type.append(device)
    
    return devices_of_type

def findDeviceByIDAndType(device_id, device_type):
    potential_device = findDeviceByID(device_id)
    if (type(potential_device.fmqtt_interface) is device_type):
        return potential_device
    else:
        return None

def deviceJSONFormat(device_mqtt_interface):
    output_str = ""

    print(device_mqtt_interface.getDeviceType())

    output_str += "\"id\": " + str(device_mqtt_interface.getDeviceID()) + ", "
    output_str += "\"device_type\" : \"" + device_mqtt_interface.getDeviceType() + "\""

    return "{" + output_str + "}"

def deviceSensorDataJSON(device_mqtt_interface):
    core_output_str = deviceJSONFormat(device_mqtt_interface)

    print(core_output_str)
    print(type(device_mqtt_interface))
    output_str = core_output_str.replace("{", "").replace("}", "") + ", "

    if (type(device_mqtt_interface) is PlantMonitorInterface):
        output_str += "\"moisture\": " + str(device_mqtt_interface.getMoisturePercentage()) + ", "
        output_str += "\"humidity\": " + str(device_mqtt_interface.getHumidity()) + ", "
        output_str += "\"temperature\": " + str(device_mqtt_interface.getTemperature())

    if (type(device_mqtt_interface) is WaterSystemInterface): 
        output_str += "\"pump_state\": \"" + str(device_mqtt_interface.getValveState()) + "\", "
        output_str += "\"total_volume\": " + str(device_mqtt_interface.getWaterVolume())

    if (type(device_mqtt_interface) is SmokeSensorInterface):
        output_str += "\"smoke_reading\": " +  str(device_mqtt_interface.getSmokeValue()) + ", "

    return "{" + output_str + "}"

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
#https://restfulapi.net/http-status-codes/

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "Welcome to Smart Garden API"

#IF NOT RETURNING ANY DATA:
#https://stackoverflow.com/questions/38804385/flask-to-return-nothing-but-only-run-script
#just return a 204 response code
@app.errorhandler(404)
def page_not_found(e):
    return ("Route Not Found", 404)

@app.route("/get_all_devices_info", methods=['GET'])
def get_all_devices_info():
    output_str = ""

    for device in connection_list:
        if output_str != "":
            output_str += ", "

        print(device.fmqtt_interface)

        if device.fmqtt_interface != None:
            output_str += deviceJSONFormat(device.fmqtt_interface)
    
    return "[" + output_str + "]"

@app.route("/get_all_devices_sensor_data", methods=['GET'])
def get_all_devices_sensor_data():
    output_str = ""

    print(connection_list)
    print(len(connection_list))

    for device in connection_list:
        if device.fmqtt_interface != None:
            if output_str != "":
                output_str += ", "

            output_str += deviceSensorDataJSON(device.fmqtt_interface)
    
    return "[" + output_str + "]"   

@app.route("/get_devices_of_type_info/<device_type_name>", methods=['GET', 'POST'])
def get_devices_of_type_info(device_type_name):
    output_str = ""

    for device in connection_list:
        if device.fmqtt_interface != None:
            if (device.fmqtt_interface.getDeviceType() == device_type_name):
                if output_str != "":
                    output_str += ", "
                output_str += deviceJSONFormat(device.fmqtt_interface)
    
    return "[" + output_str + "]"

@app.route("/flash_all_lights", methods=['GET', 'POST'])
def flash_all_lights():
    for device in connection_list:
        if device.fmqtt_interface != None:
            msg_details = getattr(device.fmqtt_interface, 'blinkLED')()
            print(msg_details)
            device.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

    return ('', 204)

@app.route("/flash_light/<device_id>", methods=['GET', 'POST'])
def flash_light_for_id(device_id):
    selected_device = findDeviceByID(device_id)

    if selected_device is None:
        return ('No Device Exists for Input ID', 400)
    else:
        msg_details = getattr(selected_device.fmqtt_interface, 'blinkLED')()
        selected_device.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

    return ('', 204)

@app.route("/change_valve_state/<device_id>/<state>", methods=['GET', 'POST'])
def turn_on_valve(device_id, state):
    selected_device = None

    if state not in ["open", "closed"]:
        return "invalid state provided"

    selected_device = findDeviceByIDAndType(device_id, WaterSystemInterface)

    if selected_device is not None:
        if state == "open":
            msg_details = getattr(selected_device.fmqtt_interface, 'openValve')()
        elif state == "closed":
            msg_details = getattr(selected_device.fmqtt_interface, 'closeValve')()
        
        print(msg_details)
        selected_device.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])
    else:
        return ('', 400)

    return ('', 204)

#TODO: see how this performs when trying to water two devices at once!
@app.route("/water_set_volume/<device_id>/<volume>", methods=['GET', 'POST'])
def water_set_volume(device_id, volume):
    selected_device = None

    selected_device = findDeviceByIDAndType(device_id, WaterSystemInterface)

    if selected_device is not None:
        msg_details = getattr(selected_device.fmqtt_interface, 'openValve')()
        print(msg_details)
        selected_device.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])
        
        while (selected_device.fmqtt_interface.getWaterVolume() <= float(volume)):
            sleep(0.2)
            print("Volume: " + str(selected_device.fmqtt_interface.getWaterVolume()))
            continue

        msg_details = getattr(selected_device.fmqtt_interface, 'closeValve')()
        selected_device.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

    return ('', 204)

#TODO: route to return all avaliable methods?

#example URL:
#/water_plant_to_target_moisture?plant_id=0&watering_id&target_moisture=20
#moisture represented as a whole number percentage
@app.route("/water_plant_to_target_moisture/", methods=['GET', 'POST'])
def water_plant_to_target_moisture():
    plant_monitor_id = request.args.get("plant_id")
    watering_system_id = request.args.get("watering_id")
    target_moisture = request.args.get("target_moisture")

    selected_plant_monitor = findDeviceByIDAndType(plant_monitor_id, PlantMonitorInterface)
    selected_watering_system = findDeviceByIDAndType(watering_system_id, WaterSystemInterface)

    if (selected_plant_monitor is None) or (selected_watering_system is None):
        return ('', 400)

    if (selected_plant_monitor.fmqtt_interface.getMoisturePercentage() <= float(target_moisture)):
        msg_details = getattr(selected_watering_system.fmqtt_interface, 'openValve')()

        selected_watering_system.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

        while (selected_plant_monitor.fmqtt_interface.getMoisturePercentage() <= float(target_moisture)):
            sleep(0.2)
            continue

        msg_details = getattr(selected_watering_system.fmqtt_interface, 'closeValve')()
        selected_watering_system.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

    return ('', 204)

#same get variables as API route above
@app.route("/bind_watering_to_plant/", methods=['GET', 'POST'])
def link_watering_to_plant():
    plant_monitor_id = request.args.get("plant_id")
    watering_system_id = request.args.get("watering_id")
    target_moisture = request.args.get("target_moisture")

    selected_plant_monitor = findDeviceByIDAndType(plant_monitor_id, PlantMonitorInterface)
    selected_watering_system = findDeviceByIDAndType(watering_system_id, WaterSystemInterface)

    if (selected_plant_monitor is None) or (selected_watering_system is None):
        return ('', 400)

    selected_watering_system.fmqtt_interface.setTriggerMoistureLevel(int(target_moisture))
    selected_watering_system.fmqtt_interface.setCoupledPlantInterface(selected_plant_monitor.fmqtt_interface)

    new_moisture_watch_thread = CoupledPlantMoistureWatcher(selected_watering_system)
    new_moisture_watch_thread.start()
    selected_watering_system.setMoistureWatcherThread(new_moisture_watch_thread)

    return ('', 204)

@app.route("/remove_bind_watering_to_plant/<plant_id>", methods=['GET', 'POST'])
def remove_bind_watering_to_plant(plant_id):
    selected_plant_monitor = findDeviceByIDAndType(plant_id, PlantMonitorInterface)

    if (selected_plant_monitor is None):
        return ('', 400)

    watering_devices = findDevicesByType(WaterSystemInterface)

    for device in watering_devices:
        if (device.fmqtt_interface.getCoupledPlantInterface() is not None):
            print(device.fmqtt_interface.getCoupledPlantInterface())
            print(device.fmqtt_interface.getCoupledPlantInterface().getDeviceID())
            print(selected_plant_monitor.fmqtt_interface.getDeviceID())

            if (device.fmqtt_interface.getCoupledPlantInterface().getDeviceID() == selected_plant_monitor.fmqtt_interface.getDeviceID()):
                msg_details = getattr(device.fmqtt_interface, 'closeValve')()
                print(msg_details)
                device.sendMsg(msg_details[PAYLOAD_MSG_KEY], msg_details["topic"])

                device.fmoisture_watcher_thread.join()

                sleep(0.5)
                device.fmoisture_watcher_thread = None

                return ('', 400)
    return ('', 400)

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
