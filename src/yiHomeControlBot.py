import logging
import os

from lib import telegramBot, botUtils, videoAnalysis, mqttClient

if __name__ == '__main__':
    # WORKING DIRECTORY
    abspath = os.path.abspath(__file__)
    d_name = os.path.dirname(abspath)
    os.chdir(d_name)

    # INIT
    botUtils.init_logger()
    logger = logging.getLogger(os.path.basename(__file__))
    config = botUtils.load_yaml("../config.yaml")
    botUtils.check_configuration(config)
    logger.info("Configuration loaded")

    # DB
    authChatIds = dict()

    # BOT
    telegram_bot = telegramBot.TelegramBot(config, authChatIds)
    # telegram_bot.startWebHook()
    telegram_bot.start_polling()

    # OPENCV
    videoAnalysis = videoAnalysis.VideoAnalysis(config, authChatIds, telegram_bot.get_bot())
    logger.info("Initialized Video-Analysis module")

    # MQTT
    mqttClient = mqttClient.MqttClient(videoAnalysis, authChatIds, telegram_bot.get_bot(), config)
    mqttClient.connect_and_start()
    logger.info("MQTT client started")
