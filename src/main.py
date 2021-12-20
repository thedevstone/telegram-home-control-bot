import logging
import os
from typing import Dict

from bot import telegram_bot
from cameras.camera import Camera
from cameras.camera_loader import CameraLoader
from mqtt import mqtt_client
from mqtt.mqtt_topic_handler import MQTTTopicHandler
from ping import ping_service
from utils import utils

if __name__ == '__main__':
    # WORKING DIRECTORY
    abspath = os.path.abspath(__file__)
    d_name = os.path.dirname(abspath)
    os.chdir(d_name)

    # INIT
    utils.init_logger()
    logger = logging.getLogger(os.path.basename(__file__))
    user_config = utils.load_yaml("../config.yaml")
    camera_types = utils.load_yaml("../camera-types.yaml")
    config = utils.merge_yaml_configs(user_config, camera_types)

    utils.check_configuration(config)
    logger.info("Configuration loaded")

    # CAMERAS
    camera_loader = CameraLoader(config)
    camera_instances: Dict[str, Camera] = camera_loader.load_camera_instances()

    # DB
    authChatIds = dict()

    # BOT
    telegram_bot = telegram_bot.TelegramBot(config, authChatIds, camera_instances)
    # telegram_bot.start_web_hook()
    telegram_bot.start_polling()

    # MQTT
    topic_handler = MQTTTopicHandler(telegram_bot.utils)
    mqttClient = mqtt_client.MqttClient(config, topic_handler)
    mqttClient.connect_and_start()

    pingService = ping_service.PingService(telegram_bot.utils, config)
    pingService.start_service_async()
