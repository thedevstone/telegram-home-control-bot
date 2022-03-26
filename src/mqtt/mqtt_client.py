import logging
import os
from random import Random
from typing import Callable

import paho.mqtt.client as mqtt

logger = logging.getLogger(os.path.basename(__file__))


class MqttClient:
    def __init__(self, config):
        self.config = config
        self.client = mqtt.Client(client_id="Bot-" + str(Random().randint(0, 1000)), clean_session=True)
        self.init_mqtt_client()

    def init_mqtt_client(self):
        username = self.config["broker-mqtt"]["username"]
        password = self.config["broker-mqtt"]["password"]
        self.client.username_pw_set(username=username, password=password)

    def set_on_connect(self, function: Callable):
        self.client.on_connect = function

    def set_on_message(self, function: Callable):
        self.client.on_message = function

    def connect_and_start(self):
        server: str = self.config["broker-mqtt"]["ip"]
        if server:
            self.client.connect(server, 1883, 60)
            self.client.loop_start()
            logger.info("MQTT client started")
        else:
            logger.warning("MQTT client not defined")

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload, qos=1)

    def disconnect_and_stop(self):
        self.client.loop_stop()
        self.client.disconnect()
