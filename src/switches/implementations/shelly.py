import logging
import os
from typing import Dict

from mqtt.mqtt_client import MqttClient
from switches.switch import Switch

logger = logging.getLogger(os.path.basename(__file__))
command_topic = "shellies/shelly-door/relay/0/command"


class Shelly(Switch):
    def __init__(self, name: str, ip: str, port: int, username: str, password: str, services: Dict):
        super().__init__(name, ip, port, username, password, services)
        self.__mqtt_client: MqttClient = self.services["mqtt"]

    def switch_on(self):
        pass

    def switch_off(self):
        pass

    def toggle(self):
        pass

    def impulse(self):
        self.__mqtt_client.publish(command_topic, "on")
