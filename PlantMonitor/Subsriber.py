import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        #Subscribing in on_connect() means that if we loose the connection and
        #reconnect then subscriptions will be renewed.
        client.subscribe([("/edge_device/PlantData",0), ("/edge_device/Picture",0)])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #create a new jpg and write payload to it
    if(msg.topic == "/edge_device/Picture"):
        f = open('output.jpg', "wb")
        f.write(msg.payload)
        print("Image Received")
        f.close()
    elif(msg.topic == "/edge_device/PlantData"):
        print(msg.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#broker is this ip
client.connect("192.168.0.11", 1883, 60)

# Blocking call that processes network traffic, disapatches callbacks and
#handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
#manual interface.
client.loop_forever()






