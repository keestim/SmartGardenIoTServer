import abc

class DeviceInterface():
    def __init__(self, topics = ""):
        self.ftopic_list = topics

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
    def __init__(self): 
        super().__init__()
        self.fTemperature = 0
        self.fMoisture = 0
        self.fHumidity = 0

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)

class WaterSystemInterface(DeviceInterface):
    def __init__(self):
        super().__init__()

        self.fWaterVolume = 0
        self.fValueOpen = False

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)