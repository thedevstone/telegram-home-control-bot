import logging
import os
from io import BytesIO

import paho.mqtt.client as mqtt

from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class MQTTTopicHandler:
    def __init__(self, config, bot_utils: BotUtils):
        self.config = config
        self.bot_utils = bot_utils
        self.topic_handlers = dict()
        self.init_handlers()

    def init_handlers(self):
        self.topic_handlers["status-message"] = self.status_message_handler
        self.topic_handlers["motion-message"] = self.motion_message_handler
        self.topic_handlers["sound-message"] = self.sound_message_handler
        self.topic_handlers["motion-image"] = self.motion_detection_image_handler

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT Connected with result code " + str(rc))
        for camera_name, camera_value in self.config["cameras"].items():
            camera_type_config = self.config["camera-types"][camera_value["type"]]
            if "mqtt" in camera_type_config:
                for topic_key, topic in camera_type_config["mqtt"]["topic-suffix"].items():
                    client.subscribe("{}/{}".format(camera_name, topic), qos=1)
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
            self.handle(topic_key=topic_key, camera=camera_name, message=msg)

    def handle(self, topic_key: str, camera: str, message: mqtt.MQTTMessage):
        try:
            self.topic_handlers[topic_key](camera, message)
        except KeyError:
            logger.warning("<{}> handler not found".format(topic_key))

    def status_message_handler(self, camera: str, message: mqtt.MQTTMessage):
        payload = self.get_text_payload(message)
        self.bot_utils.send_msg_to_logged_auth_users(camera=camera, message="{}: {}".format(camera, payload))

    def motion_message_handler(self, camera: str, message: mqtt.MQTTMessage):
        payload = self.get_text_payload(message)
        self.bot_utils.send_msg_to_logged_auth_users(camera=camera, message="{}: {}".format(camera, payload))

    def sound_message_handler(self, camera: str, message: mqtt.MQTTMessage):
        payload = self.get_text_payload(message)
        self.bot_utils.send_msg_to_logged_auth_users(camera=camera, message="{}: {}".format(camera, payload))

    def motion_detection_image_handler(self, camera: str, message: mqtt.MQTTMessage):
        logger.info("message")
        image = BytesIO(message.payload)
        self.bot_utils.send_image_to_logged_auth_users(camera=camera, image=image, caption="{}: motion".format(camera))

    @staticmethod
    def get_text_payload(message: mqtt.MQTTMessage) -> str:
        payload = str(message.payload.decode("utf-8"))
        return payload
