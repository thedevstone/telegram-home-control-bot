from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, Filters
from lib import command, botStates, botEvents
import os
import logging

logger = logging.getLogger(os.path.basename(__file__))

class TelegramBot:
    def __init__(self, config, authChatIds):
        # Constructor
        self.config = config
        self.authChatIds = authChatIds
        self.updater = Updater(token = config["token"], use_context = True)
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher
        self.command = command.Command(config, authChatIds)

        # FSM
        self.settings_handler = ConversationHandler(
            entry_points = [CallbackQueryHandler(self.command.get_log, pattern='^' + str(botEvents.LOG_CLICK) + '$'),
                            CallbackQueryHandler(self.command.face_number, pattern='^' + str(botEvents.FACES_CLICK) + '$'),
                            CallbackQueryHandler(self.command.seconds_to_analyze, pattern='^' + str(botEvents.SECONDS_CLICK) + '$'), 
                            CallbackQueryHandler(self.command.frame_percentage, pattern='^' + str(botEvents.PERCENTAGE_CLICK) + '$'), 
                            ],  
            states = {
                botStates.RESP_SETTINGS: [CallbackQueryHandler(self.command.setting_resp, pattern="^(?!" + str(botEvents.BACK_CLICK)+ ").*")]
            },
            fallbacks = [CallbackQueryHandler(self.command.exit, pattern='^' + str(botEvents.EXIT_CLICK) + '$'),
                        CallbackQueryHandler(self.command.show_settings, pattern='^' + str(botEvents.BACK_CLICK) + '$')],
            per_message=True,
            map_to_parent = {
                botStates.END: botStates.LOGGED,
                botStates.SETTINGS : botStates.SETTINGS
            }
        )

        #Level 1 only callback (no warning)
        self.menu_handler = ConversationHandler(
            entry_points = [CallbackQueryHandler(self.command.show_settings, pattern='^' + str(botEvents.SETTINGS_CLICK) + '$'),
                            CallbackQueryHandler(self.command.logout, pattern='^' + str(botEvents.LOGOUT_CLICK) + '$'),
                            ], 
            states = {
                botStates.SETTINGS: [self.settings_handler]
            },
            fallbacks = [CallbackQueryHandler(self.command.exit, pattern='^' + str(botEvents.EXIT_CLICK) + '$')],
            per_message=True,
            map_to_parent = {
                botStates.END : botStates.LOGGED,
                botStates.LOGGED: botStates.LOGGED,
                botStates.NOT_LOGGED: botStates.NOT_LOGGED
            }
        )

        #Level 0
        self.conversationHandler = ConversationHandler(
            entry_points = [CommandHandler('start', callback = self.command.start)], 
            states = {
                botStates.NOT_LOGGED : [CommandHandler('login', callback = self.command.login)],
                botStates.CREDENTIALS : [MessageHandler(filters = Filters.text, callback = self.command.credentials)],
                botStates.LOGGED :[CommandHandler('menu', callback = self.command.show_logged_menu), self.menu_handler],
            },
            fallbacks = [CallbackQueryHandler(self.command.start, pattern='^' + str(botEvents.EXIT_CLICK) + '$')]
        )

        # Init handlers
        self.dispatcher.add_handler(self.conversationHandler)
        

    def startWebHook(self):
        ######### START WEBHOOK
        network = config["network"]["telegram"]
        key = botUtils.getProjectRelativePath(network["key"])
        cert = botUtils.getProjectRelativePath(network["cert"])
        botUtils.startWebHook(updater, config["token"], network["ip"], network["port"], key, cert)
        logger.info("Started Webhook bot")

    def startPolling(self):
        logger.info("Started Polling bot")
        self.updater.start_polling()

    def getBot(self):
        return self.bot