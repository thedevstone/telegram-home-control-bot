import logging
import os
from random import Random

import paho.mqtt.client as mqtt

from mqtt.yi_mqtt_topic_handler import YiMQTTTopicHandler

logger = logging.getLogger(os.path.basename(__file__))


class MqttClient:
    def __init__(self, auth_chat_ids, bot, config, topic_handler: YiMQTTTopicHandler):
        self.authChatIds = auth_chat_ids
        self.bot = bot
        self.config = config
        self.client = mqtt.Client(client_id="Bot-" + str(Random().randint(0, 1000)), clean_session=True)
        self.topic_handler = topic_handler
        self.init_mqtt_client()

    def init_mqtt_client(self):
        username = self.config["broker-mqtt"]["username"]
        password = self.config["broker-mqtt"]["password"]
        self.client.username_pw_set(username=username, password=password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT Connected with result code " + str(rc))
        for _, camera in self.config["cameras"].items():
            for topic in camera["topics"]:
                self.client.subscribe("{}".format(topic), qos=1)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        if self.config["mqtt"]["enable"]:
            self.topic_handler.handle(msg)

    def connect_and_start(self):
        server: str = self.config["broker-mqtt"]["ip"]
        if server:
            self.client.connect(server, 1883, 60)
            self.client.loop_start()
            logger.info("MQTT client started")
        else:
            logger.warning("MQTT client not defined")

    def disconnect_and_stop(self):
        self.client.loop_stop()
        self.client.disconnect()
