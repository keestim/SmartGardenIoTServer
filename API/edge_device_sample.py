from enum import Enum  
import socket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep
import threading

from BiDirectionalMQTTComms import * 

class CommunicationInterface():
    def __init__(self, topics):
        self.ftopic_list = self.__constructTopicsList(topics)

    def getTopicList(self):
        return self.ftopic_list

    def __constructTopicsList(self, topics):
        result_arr = []
        
        for topic in topics:
            result_arr.append((topic, 0))

        return result_arr        

    def onMessage(self, topic, payload):
        print(topic + "|" + payload)


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

global server_ip_address
server_ip_address = "192.168.1.46"

if __name__ == "__main__":
    print(get_ip())
    print(server_ip_address)

    interface_obj = CommunicationInterface(["/edge_device/data", "/edge_device/setup_device"])

    mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, interface_obj)
    mqtt_connection_initalizer = MQTTConnectInitializer(mqtt_interface)
    mqtt_connection_initalizer.start()
