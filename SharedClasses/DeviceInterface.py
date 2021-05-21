import abc
from flask import json
import repackage
repackage.up()
from SharedClasses.SystemConstants import *

num_edge_devices = 0

PLANT_MONITOR_TYPE_NAME = "PlantMonitor" 
WATERING_SYSTEM_TYPE_NAME = "WateringSystem"
SMOKE_MONITOR_TYPE_NAME = "SmokeMonitor"

PAYLOAD_MSG_KEY = "payload"
TOPIC_MSG_KEY = "topic"

class DeviceInterface():
    global num_edge_devices

    def __init__(self, topics = ""):
        global num_edge_devices

        self.ftopic_list = topics
        self.fDeviceType = ""
        self.fdevice_id = num_edge_devices
        num_edge_devices += 1

    def getTopicList(self):
        return self.ftopic_list
    
    @abc.abstractmethod
    def onMessage(self, topic, payload):
        pass

    def blinkLED(self):
        output_msg = {}
        output_msg["topic"] = CONTROL_DEVICE_TOPIC
        output_msg[PAYLOAD_MSG_KEY] = "{\"blink_led\" : \"true\"}"
        return output_msg

    def getDeviceID(self):
        return self.fdevice_id

    def getDeviceType(self):
        return self.fDeviceType

class PlantMonitorInterface(DeviceInterface):
    def __init__(self): 
        super().__init__()
        self.fTemperature = 0
        self.fHumidity = 0
        self.fMoistureRaw = 0
        self.fMoisturePercentage = 0
        self.fDeviceType = PLANT_MONITOR_TYPE_NAME
        
    def onMessage(self, topic, payload):
        if (topic == PLANT_INFO_TOPIC):
            device_data = json.loads(payload)
            self.fHumidity = int(device_data["humidity"]) 
            self.fMoistureRaw = device_data["moisture"]
            self.fMoisturePercentage = (self.fMoistureRaw / 850) * 100
            self.fTemperature = device_data["temperature"]

    def getTemperature(self):
        return self.fTemperature

    def getMoistureRaw(self):
        return self.fMoistureRaw

    def getMoisturePercentage(self):
        return self.fMoisturePercentage

    def getHumidity(self):
        return self.fHumidity

class WaterSystemInterface(DeviceInterface):
    def __init__(self):
        super().__init__()

        self.fWaterVolume = 0
        self.fValueOpen = False
        self.fDeviceType = WATERING_SYSTEM_TYPE_NAME
        
        self.fCoupledPlantInterface = None
        self.fTriggerMoistureLevel = 0

    def onMessage(self, topic, payload):
        if (topic == WATERING_INFO_TOPIC):
            device_data = json.loads(payload)
            self.fValueOpen = str(device_data["pump_state"]) == "1"
            self.fWaterVolume = float(device_data["total_volume"])

    def getWaterVolume(self):
        return self.fWaterVolume
        
    def getValveState(self):
        return self.fValueOpen

    def openValve(self):
        output_msg = {}
        output_msg["topic"] = CONTROL_DEVICE_TOPIC
        output_msg[PAYLOAD_MSG_KEY] = "{\"valve_state\" : \"open\"}"
        return output_msg

    def closeValve(self):
        output_msg = {}
        output_msg["topic"] = CONTROL_DEVICE_TOPIC
        output_msg[PAYLOAD_MSG_KEY] = "{\"valve_state\" : \"closed\"}"
        return output_msg

    def getCoupledPlantInterface(self):
        return self.fCoupledPlantInterface

    def setCoupledPlantInterface(self, input_interface):
        self.fCoupledPlantInterface = input_interface

    def getTriggerMoistureLevel(self):
        return self.fTriggerMoistureLevel

    def setTriggerMoistureLevel(self, input_value):
        self.fTriggerMoistureLevel = input_value

class SmokeSensorInterface(DeviceInterface):
    def __init__(self): 
        super().__init__()
        self.fSmokeValue = 0
        self.fDeviceType = SMOKE_MONITOR_TYPE_NAME
        
    def onMessage(self, topic, payload):
        if (topic == SMOKE_INFO_TOPIC):
            device_data = json.loads(payload)
            self.fSmokeValue = int(device_data["smoke_reading"]) 

    def getSmokeValue(self):
        return self.fSmokeValue