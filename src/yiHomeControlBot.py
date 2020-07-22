from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import bot
import os
from pathlib import Path
import logging
from lib import commands, botUtils, osWatcher, videoAnalysis, pollingWatcher
import json
import yaml
import time
import threading

########### WORKING DIRECTORY
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

############ INIT
botUtils.initLogger()
logger = logging.getLogger(os.path.basename(__file__))
config = botUtils.loadYaml("../config.yaml")
logger.info("Configuration loaded")

######### DB
authChatIds = dict()

botUtils.checkConfiguration(config)
########## BOT
updater = Updater(token = config["token"], use_context = True)
bot = updater.bot
dispatcher = updater.dispatcher

command = commands.Command(config, authChatIds)

# HANDLERS
CREDENTIALS, LOGGED, SETTINGS = range(3)
SETTINGS_RESP, END = range(3, 5)

settings_handler = ConversationHandler(
    entry_points = [CallbackQueryHandler(callback = command.settings)], 
    states = {
        SETTINGS_RESP: [CallbackQueryHandler(callback = command.setting_resp, )]
    },
    fallbacks= {},
    per_message=True,
    map_to_parent = {
        END: LOGGED
    }
)

conversationHandler = ConversationHandler(
    entry_points = [CommandHandler('start', callback = command.start)], 
    states = {
        CREDENTIALS : [MessageHandler(filters = Filters.text, callback = command.credentials)],
        LOGGED :[CommandHandler('settings', callback = command.show_settings),
                CommandHandler('logout', callback = command.logout)
        ],
        SETTINGS: [settings_handler]
    },
    fallbacks= {}
)

dispatcher.add_handler(conversationHandler)

######### START WEBHOOK
network = config["network"]
key = botUtils.getProjectRelativePath(network["key"])
cert = botUtils.getProjectRelativePath(network["cert"])
botUtils.startWebHook(updater, config["token"], network["ip"], network["port"], key, cert)
#updater.start_polling()
logger.info("Started Webhook bot")

########## OPENCV
videoAnalysis = videoAnalysis.VideoAnalysis(config)
logger.info("Initialized Video-Analysis module")

########## OS WATCHER
watch_directory = config["watchDirectory"]
if (not os.path.isabs(watch_directory)):
    watch_directory = os.path.abspath(os.path.join(watch_directory, ".."))
#watcher = osWatcher.Watcher(watch_directory, videoAnalysis, authChatIds, bot)
watcher = pollingWatcher.Watcher(watch_directory, videoAnalysis, authChatIds, bot, config)
thread1 = threading.Thread(watcher.checkFolder())
thread1.start()
logger.info("File watchdog started")