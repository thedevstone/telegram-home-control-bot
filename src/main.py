import logging
import os

from bot import telegram_bot
from mqtt import mqtt_client
from utils import utils
from video import video_analysis

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
    # telegram_bot.startWebHook()
    telegram_bot.start_polling()

    # OPENCV
    videoAnalysis = video_analysis.VideoAnalysis(config, authChatIds, telegram_bot.utils)
    logger.info("Initialized Video-Analysis module")

    # MQTT
    mqttClient = mqtt_client.MqttClient(videoAnalysis, authChatIds, telegram_bot.get_bot(), config)
    mqttClient.connect_and_start()
    logger.info("MQTT client started")
