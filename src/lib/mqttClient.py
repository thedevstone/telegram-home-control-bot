import os
import glob
from lib import botUtils, videoAnalysis
import threading
import time
import matplotlib.pyplot as plt
import matplotlib
import cv2
import logging
import telegram
from PIL import Image
from io import BytesIO
import paho.mqtt.client as mqtt

logger = logging.getLogger(os.path.basename(__file__))

class MqttClient:
    def __init__(self, videoAnalysis, authChatIds, bot, config):
        self.videoAnalysis = videoAnalysis
        self.authChatIds = authChatIds
        self.bot = bot
        self.config = config
        self.client = mqtt.Client(client_id="Bot", clean_session=True)
        self.initMqttClient()
        
    def initMqttClient(self):
        username = self.config["network"]["mqtt"]["username"]
        password = self.config["network"]["mqtt"]["password"]
        self.client.username_pw_set(username=username, password=password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT Connected with result code " + str(rc))
        for key, value in self.config["network"]["cameras"].items():
            self.client.subscribe("{}".format(value["topic"]), qos=1)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        message = str(msg.payload.decode("utf-8"))
        camera_id = str(msg.topic).split('/')[0]
        status = self.config["analysis"]["status"]
        if (message == "motion_start" and status) : self.motionStart(camera_id)

    def connectAndStart(self):
        server = self.config["network"]["mqtt"]["server"]
        self.client.connect(server, 1883, 60)
        self.client.loop_start()
    
    def disconnectAndStop(self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def motionStart(self, camera_id):
        print("motion detected")
        self.videoAnalysis.analyzeRTSP(camera_id)
    

