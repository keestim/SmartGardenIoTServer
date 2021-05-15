from flask import Flask, request, jsonify
import threading
import pyshark
from time import sleep  
from helper_functions import *
import sys

from BiDirectionalMQTTComms import * 
class MQTTSniffer(threading.Thread):
    def __init__(self, interfacename):
        super().__init__()
        self.fmqtt_ip_addresses = []
        self.fdevice_ip_address = get_ip()
        self.fcapture = pyshark.LiveCapture(interface = interfacename)
        self.fconnection_list = []

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
                    self.fconnection_list.append(new_mqtt_connection)

                    print(len(self.fconnection_list))
            except:
                print("Issue with network or adding MQTT bi directional connection")

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "API Test"

@app.route("/probe_devices", methods=['GET'])
def probe_devices():
    devices_str = ""

    for device in mqtt_sniffer.fconnection_list:
        devices_str = devices_str + device.fdest_ip_address + ", "
        device.sendMsg("The bois")

    return devices_str

if __name__ == "__main__":
    try:
        server_network_interface = sys.argv[1]
    except:
        print("You must enter the network interface that you're connected through")
        exit()

    mqtt_sniffer = MQTTSniffer(server_network_interface)
    mqtt_sniffer.start()
    app.run()

#maybe something to add to note either client or server side