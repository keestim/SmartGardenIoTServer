from flask import Flask, request, jsonify
import threading
import pyshark
import socket
from time import sleep  

from BiDirectionalMQTTComms import * 
class MQTTSniffer(threading.Thread):
    def __init__(self, connection_list):
        super().__init__()
        self.fmqtt_ip_addresses = []
        self.fdevice_ip_address = self.get_ip()
        self.fcapture = pyshark.LiveCapture(interface='enp0s25')
        self.fconnection_list = connection_list

    def run(self):
        for item in self.fcapture.sniff_continuously():
            try:
                mqtt_data = item.mqtt
                ip_data = item.ip

                if (ip_data.src not in self.fmqtt_ip_addresses) and not(ip_data.src == self.fdevice_ip_address):
                    self.fmqtt_ip_addresses.append(ip_data.src)

                    print(mqtt_data)
                    print("New IP: " + ip_data.src)
                    
                    print("New Connection")
                    new_mqtt_connection = BiDirectionalMQTTComms(self.fdevice_ip_address, ip_data.src)
                    
                    print("starting backup comms")
                    mqtt_connection_initalizer = MQTTConnectInitializer(new_mqtt_connection)
                    mqtt_connection_initalizer.start()

                    self.fconnection_list.append(new_mqtt_connection)

                    print(len(self.fconnection_list))

            except:
                continue

    #Source: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    def get_ip(self):
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

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "API Test"

if __name__ == "__main__":
    active_mqtt_connections = []
    mqtt_sniffer = MQTTSniffer(active_mqtt_connections)
    mqtt_sniffer.start()
    app.run()
