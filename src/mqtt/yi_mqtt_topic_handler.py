import logging
import os
from io import BytesIO

import paho.mqtt.client as mqtt

from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class YiMQTTTopicHandler:
    def __init__(self, bot_utils: BotUtils):
        self.bot_utils = bot_utils
        self.topic_handlers = dict()
        self.init_handlers()

    def init_handlers(self):
        # self.topic_handlers["motion_detection"] = self.motion_message_handler
        # self.topic_handlers["status"] = self.status_message_handler
        # self.topic_handlers["sound_detection"] = self.motion_message_handler
        self.topic_handlers["motion_detection_image"] = self.motion_detection_image_handler

    def handle(self, message: mqtt.MQTTMessage):
        split = str(message.topic).split('/')
        camera = split[0]
        topic = split[1]
        try:
            self.topic_handlers[topic](camera, message)
        except KeyError:
            logger.warning("<{}> handler not found".format(topic))

    def status_message_handler(self, camera: str, message: mqtt.MQTTMessage):
        payload = self.get_text_payload(message)
        self.bot_utils.send_msg_to_logged_users(message="{} from {}".format(payload, camera))

    def motion_message_handler(self, camera: str, message: mqtt.MQTTMessage):
        payload = self.get_text_payload(message)
        self.bot_utils.send_msg_to_logged_users(message="{} from {}".format(payload, camera))

    def motion_detection_image_handler(self, camera: str, message: mqtt.MQTTMessage):
        image = BytesIO(message.payload)
        self.bot_utils.send_image_to_logged_users(image=image, caption="motion: {}".format(camera))

    @staticmethod
    def get_text_payload(message: mqtt.MQTTMessage) -> str:
        payload = str(message.payload.decode("utf-8"))
        return payload
