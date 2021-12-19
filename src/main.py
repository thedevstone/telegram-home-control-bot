import logging
import os

from bot import telegram_bot
from mqtt import mqtt_client
from mqtt.mqtt_topic_handler import MQTTTopicHandler
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

    # DB
    authChatIds = dict()

    # BOT
    telegram_bot = telegram_bot.TelegramBot(config, authChatIds)
    # telegram_bot.start_web_hook()
    telegram_bot.start_polling()

    # MQTT
    topic_handler = MQTTTopicHandler(bot_utils=telegram_bot.utils)
    mqttClient = mqtt_client.MqttClient(authChatIds, telegram_bot.get_bot(), config, topic_handler)
    mqttClient.connect_and_start()
