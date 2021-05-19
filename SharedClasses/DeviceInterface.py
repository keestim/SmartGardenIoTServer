import abc
from flask import json
import repackage
repackage.up()
from SharedClasses.BiDirectionalMQTTComms import * 

num_edge_devices = 0

class DeviceInterface():
    global num_edge_devices
    def __init__(self, topics = ""):
        global num_edge_devices

        self.ftopic_list = topics
        self.fDeviceType = ""
        self.fdevice_id = num_edge_devices
        num_edge_devices = num_edge_devices + 1

    def getTopicList(self):
        return self.ftopic_list
    
    @abc.abstractmethod
    def onMessage(self, topic, payload):
        pass

    def blinkLED(self):
        output_msg = {}
        output_msg["topic"] = CONTROL_DEVICE_TOPIC
        output_msg["payload"] = "{\"blink_led\" : \"true\"}"
        return output_msg

    def getDeviceID(self):
        return self.fdevice_id

    def getDeviceType(self):
        return self.fDeviceType

class PlantMonitorInterface(DeviceInterface):
    def __init__(self): 
        super().__init__()
        self.fTemperature = 0
        self.fMoisture = 0
        self.fHumidity = 0
        self.fDeviceType = "PlantMonitor"
        
    def onMessage(self, topic, payload):
        print(topic + "|" + payload)

        if (topic == "/edge_device/PlantData"):
            device_data = json.loads(payload)
            self.fHumidity = device_data["humidity"]
            self.fMoisture = device_data["moisture"]
            self.fTemperature = device_data["temperature"]

    def getTemperature(self):
        return self.fTemperature

    def getMoisture(self):
        return self.fMoisture

    def getHumidity(self):
        return self.fHumidity

class WaterSystemInterface(DeviceInterface):
    def __init__(self):
        super().__init__()

        self.fWaterVolume = 0
        self.fValueOpen = False
        self.fDeviceType = "WaterSystem"

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)
        if (topic == "/edge_device/water_info"):
            device_data = json.loads(payload)
            self.fValueOpen = str(device_data["pump_state"]) == "1"
            self.fWaterVolume = float(device_data["total_volume"])

            print("Updated Private Fields for Watering Device!")

    def getWaterVolume(self):
        return self.fWaterVolume
        
    def getValveState(self):
        return self.fValueOpen

    def openValve(self):
        output_msg = {}
        output_msg["topic"] = CONTROL_DEVICE_TOPIC
        output_msg["payload"] = "{\"valve_state\" : \"open\"}"
        return output_msg

    def closeValve(self):
        output_msg = {}
        output_msg["topic"] = CONTROL_DEVICE_TOPIC
        output_msg["payload"] = "{\"valve_state\" : \"closed\"}"
        return output_msg
