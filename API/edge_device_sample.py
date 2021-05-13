from enum import Enum  
import socket

class ConnectionStatus(Enum):
    init = 1
    attempting_connection = 2
    connected = 3

#Source: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class BiDirectionalMQTTComms:
    def __init__(self, topic, device_ip_address, dest_ip_address, port = 1883, keepAlive = 60):
        self.fdest_ip_address = dest_ip_address
        self.fdevice_ip_address = device_ip_address

        self.ftopic = topic

        self.fport = port
        self.fkeepAlive = keepAlive

        self.client = None
        self.__setupReader()
        
    def __onConnect(self, client, userData, flags, responseCode):
        self.client.subscribe("/edge_device/setup_device")
        self.client.subscribe("/edge_device/data")

    def __onMessage(self, client, userData, msg):
        print(msg.topic + ", " + str(msg.payload))

    def __setupReader(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.__onConnect
        self.client.on_message = self.__onMessage

        self.client.connect(self.fdevice_ip_address, self.fport, self.fkeepAlive)
        self.client.loop_forever()

    def sendMsg(self, msgText):
        publish.single(self.fdest_ip_address, msgText, hostname = self.fipAddress)

global server_ip_address
server_ip_address = "192.168.1.46"

if __name__ == "__main__":
    mqtt_interface = BiDirectionalMQTTComms("", get_ip(), server_ip_address)
