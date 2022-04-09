import logging

import paho.mqtt.properties
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from mqtt.mqtt_client import MqttClient


class MqttLoggingHandler(logging.Handler):
    def __init__(self, mqtt_client: MqttClient):
        super().__init__()
        self.mqtt_log_topic = "bot/y-hack-telegram-bot/log"
        self.mqtt_client = mqtt_client

    def emit(self, record: logging.LogRecord) -> None:
        publish_properties = Properties(PacketTypes.PUBLISH)
        publish_properties.MessageExpiryInterval = 604800  # sec in a week
        self.mqtt_client.publish(self.mqtt_log_topic, record.message, qos=2, retain=True, properties=publish_properties)
