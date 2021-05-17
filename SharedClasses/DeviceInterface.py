import abc

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
        output_msg["topic"] = "edge_devices/control_device"
        output_msg["payload"] = "blink_led"
        return output_msg

    def getDeviceID(self):
        return self.fdevice_id

class PlantMonitorInterface(DeviceInterface):
    def __init__(self): 
        super().__init__()
        self.fTemperature = 0
        self.fMoisture = 0
        self.fHumidity = 0
        self.fDeviceType = "PlantMonitor"
        
    def onMessage(self, topic, payload):
        print(topic + "|" + payload)

class WaterSystemInterface(DeviceInterface):
    def __init__(self):
        super().__init__()

        self.fWaterVolume = 0
        self.fValueOpen = False
        self.fDeviceType = "WaterSystem"

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)

    def openValve(self):
        output_msg = {}
        output_msg["topic"] = "edge_devices/control_device"
        output_msg["payload"] = "{\"valve_state\" : \"open\"}"
        return output_msg

    def closeValve(self):
        output_msg = {}
        output_msg["topic"] = "edge_devices/control_device"
        output_msg["payload"] = "{\"valve_state\" : \"closed\"}"
        return output_msg