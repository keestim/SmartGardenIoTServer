from enum import Enum
import socket
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from time import sleep
import threading
import sys
import serial
from picamera import PiCamera
from time import sleep
import datetime

import repackage
repackage.up()
from SharedClasses.BiDirectionalMQTTComms import *
from SharedClasses.DeviceInterface import *
from SharedClasses.helper_functions import *

#####################################communicationInterface class##################################################
class CommunicationInterface():
	def __init__(self, device_type, topics):
		self.ftopic_list = topics
		self.fdevice_type = device_type
		self.fplantData = " "
		self.farduino = serial.Serial('/dev/ttyACM0', 9600)

	def getTopicList(self):
		return self.ftopic_list

	def getDeviceType(self):
		return self.fdevice_type

	def onMessage(self, topic, payload):
		#fix handling here!
		self.farduino.write(payload.encode('utf_8'))

	def getArdiuno(self):
		return self.farduino

	def readArdinoSerial(self):
		try:
			avaliable_msg = self.farduino.inWaiting()
			print(avaliable_msg)
			return self.farduino.read(avaliable_msg).decode() 
		except:
			return ""

	def getDate(self):
		return datetime.datetime.now().strftime('%m-%d-%Y_%H.%M.%S')

	def setPlantData(self, value):
		self.fplantData = value

	def getPlantData(self):
		return self.fplantData

	def capture_photo(self, img_path = '/home/pi/Desktop/images/'):
		#setup variables
		camera = PiCamera()
		capture_img_path = img_path + 'picture_' + self.getDate() + '.jpg'

		#annotates picture with date
		camera.annotate_text = self.getDate()

		#capture image
		camera.capture(capture_img_path)
		return capture_img_path

	def getCameraDataMsg(self, img_path):
		f = open(img_path, "rb")
		fileContent = f.read()
		byteArr = bytearray(fileContent)
		return byteArr

###############################################################################################################

############################################ MAIN #############################################################
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
						PLANT_MONITOR_TYPE_NAME, 
						[DEFAULT_DATA_TOPIC, 
						CONTROL_DEVICE_TOPIC, 
						SETUP_DEVICE_TOPIC, 
						"/edge_device/topic_stream",
						PLANT_INFO_TOPIC,
						"/edge_data/Picture"])

	mqtt_interface = BiDirectionalMQTTComms(get_ip(), server_ip_address, DeviceType.edge_device, interface_obj)

	while True:
		msg = interface_obj.readArdinoSerial()

		if len(msg) > 0:
			print(msg)
			interface_obj.setPlantData(msg)

			mqtt_interface.sendMsg(interface_obj.getPlantData(), PLANT_INFO_TOPIC)

		sleep(0.2)
