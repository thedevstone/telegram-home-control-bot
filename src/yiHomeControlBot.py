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
CREDENTIALS, LOGGED, NOT_LOGGED, END = range(4)

SETTINGS, RESP_SETTINGS = range(4, 6)

# Selection Level 1 Menu
SETTINGS_CLICK, LOGOUT_CLICK, EXIT_CLICK, BACK_CLICK = map(chr, range(20, 24))

# Selection Level 2 Settings
LOG_CLICK, FACES_CLICK, SECONDS_CLICK, PERCENTAGE_CLICK  = map(chr, range(10, 14))

settings_handler = ConversationHandler(
    entry_points = [CallbackQueryHandler(command.get_log, pattern='^' + str(LOG_CLICK) + '$'),
                    CallbackQueryHandler(command.face_number, pattern='^' + str(FACES_CLICK) + '$'),
                    CallbackQueryHandler(command.seconds_to_analyze, pattern='^' + str(SECONDS_CLICK) + '$'), 
                    CallbackQueryHandler(command.frame_percentage, pattern='^' + str(PERCENTAGE_CLICK) + '$'), 
                    ],  
    states = {
        RESP_SETTINGS: [CallbackQueryHandler(command.setting_resp, pattern="^(?!" + str(BACK_CLICK)+ ").*")]
    },
    fallbacks = [CallbackQueryHandler(command.exit, pattern='^' + str(EXIT_CLICK) + '$'),
                CallbackQueryHandler(command.show_settings, pattern='^' + str(BACK_CLICK) + '$')],
    per_message=True,
    map_to_parent = {
        END: LOGGED,
        SETTINGS : SETTINGS
    }
)

#Level 1 only callback (no warning)
menu_handler = ConversationHandler(
    entry_points = [CallbackQueryHandler(command.show_settings, pattern='^' + str(SETTINGS_CLICK) + '$'),
                    CallbackQueryHandler(command.logout, pattern='^' + str(LOGOUT_CLICK) + '$'),
                    ], 
    states = {
        SETTINGS: [settings_handler]
    },
    fallbacks = [CallbackQueryHandler(command.exit, pattern='^' + str(EXIT_CLICK) + '$')],
    per_message=True,
    map_to_parent = {
        END : LOGGED,
        LOGGED: LOGGED,
        NOT_LOGGED: NOT_LOGGED
    }
)

#Level 0
conversationHandler = ConversationHandler(
    entry_points = [CommandHandler('start', callback = command.start)], 
    states = {
        NOT_LOGGED : [CommandHandler('login', callback = command.login)],
        CREDENTIALS : [MessageHandler(filters = Filters.text, callback = command.credentials)],
        LOGGED :[CommandHandler('menu', callback = command.show_logged_menu), menu_handler],
    },
    fallbacks = [CallbackQueryHandler(command.start, pattern='^' + str(EXIT_CLICK) + '$')],
    allow_reentry=True
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