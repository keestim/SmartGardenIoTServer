import serial
import MySQLdb
import time
import sys
import datetime

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

device = '/dev/ttyACM0'

arduino = serial.Serial(device, 9600)

flowrate = 0
valvePos = 0

#MQTT

topic = "/edge_device/mainsConnection"
ipAddress = "192.168.20.167" #Ip address of the main edge device

def on_connect(client, userdata, flags, rc):
#print("Connected with result code "+str(rc))
client.subscribe(topic)

def on_message(client, userdata, msg):
arduino.write(msg.payload)
print(msg.topic + " " + str(msg.payload))

#MQTT

while True:
flowrate, valvePos = map(float, arduino.readline().split())

publish.single(topic, flowrate + " " + valvePos, hostname="192.168.20.36") # Sending arduino code to main edge server

time.sleep(1)

client = mqtt.Client("edgedeviceMains")
client.on_connect = on_connect
client.on_message = on_message
client.connect(ipAddress, 1883, 60)
client.loop_start()