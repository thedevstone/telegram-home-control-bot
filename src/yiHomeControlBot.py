import logging
import os

from lib import telegramBot, utils, videoAnalysis, mqttClient

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
    telegram_bot = telegramBot.TelegramBot(config, authChatIds)
    # telegram_bot.startWebHook()
    telegram_bot.start_polling()

    # OPENCV
    videoAnalysis = videoAnalysis.VideoAnalysis(config, authChatIds, telegram_bot)
    logger.info("Initialized Video-Analysis module")

    # MQTT
    mqttClient = mqttClient.MqttClient(videoAnalysis, authChatIds, telegram_bot.get_bot(), config)
    mqttClient.connect_and_start()
    logger.info("MQTT client started")
