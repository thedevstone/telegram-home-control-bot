from telegram import bot
import os
from pathlib import Path
import logging
import json
import yaml
import time
import threading
from lib import telegramBot, botUtils, videoAnalysis, mqttClient

########### WORKING DIRECTORY
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

############ INIT
botUtils.initLogger()
logger = logging.getLogger(os.path.basename(__file__))
config = botUtils.loadYaml("../config.yaml")
botUtils.checkConfiguration(config)
logger.info("Configuration loaded")

######### DB
authChatIds = dict()

########## BOT
telegram_bot = telegramBot.TelegramBot(config, authChatIds)
#telegram_bot.startPolling()
telegram_bot.startWebHook()

########## OPENCV
videoAnalysis = videoAnalysis.VideoAnalysis(config)
#videoAnalysis.analyzeRTSP("yicam-1")
logger.info("Initialized Video-Analysis module")

#MQTT
mqttClient = mqttClient.MqttClient(videoAnalysis, authChatIds, telegram_bot.getBot(), config)
mqttClient.connectAndStart()
logger.info("MQTT client started")