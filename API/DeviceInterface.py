import abc

num_plant_devices = 0
num_watering_devices = 0

class DeviceInterface():
    def __init__(self, topics = ""):
        self.ftopic_list = topics
        self.fDeviceType = ""
        self.ftype_id = 0

    def getTopicList(self):
        return self.ftopic_list
    
    @abc.abstractmethod
    def onMessage(self, topic, payload):
        pass

    def blinkLED(self):
        output_msg = {}
        output_msg["topic"] = "edge_devices/control_device"
        output_msg["payload"] = "blink_led"
        return output_msg

class PlantMonitorInterface(DeviceInterface):
    global num_plant_devices

    def __init__(self): 
        super().__init__()
        global num_plant_devices
        
        self.fTemperature = 0
        self.fMoisture = 0
        self.fHumidity = 0
        self.fDeviceType = "PlantMonitor"
        
        self.ftype_id = num_plant_devices
        num_plant_devices = num_plant_devices + 1

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)

class WaterSystemInterface(DeviceInterface):
    global num_watering_devices
    
    def __init__(self):
        super().__init__()
        global num_watering_devices

        self.fWaterVolume = 0
        self.fValueOpen = False
        self.fDeviceType = "WaterSystem"

        self.ftype_id = num_watering_devices
        num_watering_devices = num_watering_devices + 1

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)