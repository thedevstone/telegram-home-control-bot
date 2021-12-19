import logging
import os
from random import Random

import paho.mqtt.client as mqtt

from mqtt.mqtt_topic_handler import MQTTTopicHandler

logger = logging.getLogger(os.path.basename(__file__))


class MqttClient:
    def __init__(self, auth_chat_ids, bot, config, topic_handler: MQTTTopicHandler):
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
        for camera_name, camera_value in self.config["cameras"].items():
            camera_type_config = self.config["camera-types"][camera_value["type"]]
            for topic_key, topic in camera_type_config["mqtt"]["topic-suffix"].items():
                self.client.subscribe("{}/{}".format(camera_name, topic), qos=1)
                logger.info("Subscribed to {} -> {}/{}".format(topic_key, camera_name, topic))

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        split = str(msg.topic).split('/')
        camera_name = split[0]
        topic_value = split[1]
        # Get camera type settings
        camera_config = self.config["cameras"][camera_name]
        camera_type = self.config["camera-types"][camera_config["type"]]
        # Reverse topic key-value -> value-key => relative handling by keys
        topic_value_key = {v: k for k, v in camera_type["mqtt"]["topic-suffix"].items()}
        # Finally get the relative/generic topic key
        topic_key = topic_value_key[topic_value]
        if self.config["broker-mqtt"]["enable"] and topic_key in camera_config["topics"]:
            self.topic_handler.handle(topic_key=topic_key, camera=camera_name, message=msg)

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
