import logging
import os
import time
from random import Random
from typing import Callable

import paho.mqtt.client as mqtt

logger = logging.getLogger(os.path.basename(__file__))


class MqttClient:
    def __init__(self, config):
        self.config = config
        self.client = mqtt.Client(client_id="Bot-" + str(Random().randint(0, 1000)), protocol=mqtt.MQTTv5)
        self.init_mqtt_client()

    def init_mqtt_client(self):
        username = self.config["broker-mqtt"]["username"]
        password = self.config["broker-mqtt"]["password"]
        self.client.username_pw_set(username=username, password=password)

    def set_on_connect(self, function: Callable):
        self.client.on_connect = function

    def set_on_message(self, function: Callable):
        self.client.on_message = function

    def __on_disconnect(self):
        time.sleep(50)
        self.client.reconnect()

    def connect_and_start(self):
        server: str = self.config["broker-mqtt"]["ip"]
        if server:
            self.client.connect(server, 1883, 60)
            self.client.loop_start()
            self.client.on_disconnect(self.__on_disconnect())
            logger.info("MQTT client started")
        else:
            logger.warning("MQTT client not defined")

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload, qos=1)

    def disconnect_and_stop(self):
        self.client.loop_stop()
        self.client.disconnect()
