import logging
import os

from bot import telegram_bot
from mqtt import mqtt_client
from mqtt.yi_mqtt_topic_handler import YiMQTTTopicHandler
from utils import utils

if __name__ == '__main__':
    # WORKING DIRECTORY
    abspath = os.path.abspath(__file__)
    d_name = os.path.dirname(abspath)
    os.chdir(d_name)

    # INIT
    utils.init_logger()
    logger = logging.getLogger(os.path.basename(__file__))
    config = utils.load_yaml("../config.yaml")
    utils.check_configuration(config)
    logger.info("Configuration loaded")

    # DB
    authChatIds = dict()

    # BOT
    telegram_bot = telegram_bot.TelegramBot(config, authChatIds)
    telegram_bot.start_web_hook()
    # telegram_bot.start_polling()

    # MQTT
    topic_handler = YiMQTTTopicHandler(bot_utils=telegram_bot.utils)
    mqttClient = mqtt_client.MqttClient(authChatIds, telegram_bot.get_bot(), config, topic_handler)
    mqttClient.connect_and_start()
    logger.info("MQTT client started")
