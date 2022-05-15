import logging
import os
import time
from random import Random
from typing import Callable

import paho.mqtt.client as mqtt
import paho.mqtt.properties

logger = logging.getLogger(os.path.basename(__file__))


class MqttClient:
    def __init__(self, config):
        self.config = config
        self.client = mqtt.Client(client_id="Bot-" + str(Random().randint(0, 1000)), protocol=mqtt.MQTTv311)
        self.init_mqtt_client()

    def init_mqtt_client(self):
        username = self.config["broker-mqtt"]["username"]
        password = self.config["broker-mqtt"]["password"]
        self.client.username_pw_set(username=username, password=password)

    def set_on_connect(self, function: Callable):
        self.client.on_connect = function

    def set_on_message(self, function: Callable):
        self.client.on_message = function

    @staticmethod
    def on_disconnect():
        logger.warning("MQTT disconnected")

    def connect_and_start(self):
        server: str = self.config["broker-mqtt"]["ip"]
        if server:
            self.client.connect(server, 1883, 60)
            self.client.loop_start()
            self.client.on_disconnect = self.on_disconnect
            logger.info("MQTT client started")
        else:
            logger.warning("MQTT client not defined")

    def publish(self, topic: str, payload: str, qos=1, retain=False,
                properties: paho.mqtt.properties.Properties = None):
        info = self.client.publish(topic, payload, qos=qos, retain=retain, properties=properties)
        logger.info(f"Publishing: {payload} on topic {topic} - published: {info.is_published()}")

    def disconnect_and_stop(self):
        self.client.loop_stop()
        self.client.disconnect()
