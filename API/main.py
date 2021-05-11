from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import paho.mqtt.client as publish

class MQTTReader:
    def __init__(self, topic, ipAddress, port = 1883, keepAlive = 60):
        self.fipAddress = ipAddress
        self.fport = port
        self.ftopic = topic
        self.fkeepAlive = keepAlive
        self.client = self.__setupReader()
        
    def __setupReader(self):
        result = mqtt.Client()
        result.on_connect = self.__onConnect
        result.on_message = self.__onMessage
        result.connect(self.fipAddress, self.fport, self.fkeepAlive)

        result.loop_forever()

    def __onConnect(self, client, userData, flags, responseCode):
        self.client.subscribe(self.topic)

    def __onMessage(self, client, userData, msg):
        print(msg)

class MQTTWriter():
    def __init__(self, ipAddress, topic):
        self.fipAddrerss = ipAddress
        self.ftopic = topic

    def sendMsg(self, msgText):
        publish.single(self.fipAddrerss, msgText, hostname = self.fipAddrerss)

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])




app.run()