from enum import Enum
import socket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep
import threading
import sys
import serial
from time import sleep
import datetime

import repackage
repackage.up()
from SharedClasses.BiDirectionalMQTTComms import *
from SharedClasses.DeviceInterface import *
from SharedClasses.helper_functions import *

class CommunicationInterface():
	def __init__(self, device_type, topics):
		self.ftopic_list = topics
		self.fdevice_type = device_type
		self.fsmokeData = ""
		self.farduino = serial.Serial('/dev/ttyS0', 9600)

	def getTopicList(self):
		return self.ftopic_list

	def getDeviceType(self):
		return self.fdevice_type

	def onMessage(self, topic, payload):
		print("sending..."+topic + "|" + payload)
		#fix handling here!
		self.getArduinoConnection().write(payload.encode('utf_8'))

	def getArduinoConnection(self):
		return self.farduino

	def getDate(self):
		return datetime.datetime.now().strftime('%m-%d-%Y_%H.%M.%S')

	def setSmokeData(self, value):
		self.fsmokeData = value

	def getSmokeData(self):
		return self.fsmokeData

global server_ip_address
if __name__ == "__main__":
	try:
		server_ip_address = sys.argv[1]
	except:
		print("You must enter the server ip address as an additional command line arg")
		exit()

	print(get_ip())
	print(server_ip_address)

	#try make this constant!
	interface_obj = CommunicationInterface(
						SMOKE_MONITOR_TYPE_NAME, 
						[DEFAULT_DATA_TOPIC, 
						CONTROL_DEVICE_TOPIC, 
						SETUP_DEVICE_TOPIC, 
						"/edge_device/topic_stream",
						"/edge_device/SmokeData"])

	mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, DeviceType.edge_device, interface_obj)

	while True:
		interface_obj.getArduinoConnection().flush()

		#data read in
		interface_obj.setSmokeData(interface_obj.getArduinoConnection().readline().decode())

		print("Smoke Data: %s" % (interface_obj.getSmokeData()))

		#send plant data
		mqtt_interface.sendMsg(interface_obj.getSmokeData(), "/edge_device/SmokeData")
