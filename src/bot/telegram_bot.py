import logging
import os

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram.ext import Updater

from bot.conversation import root
from bot.conversation.fsm import bot_states, bot_events
from bot.conversation.settings import settings
from bot.conversation.snapshot import snapshot
from bot.utils import bot_utils
from utils import utils

logger = logging.getLogger(os.path.basename(__file__))


class TelegramBot:
    def __init__(self, config, auth_chat_ids):
        # Constructor
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.updater = Updater(token=config["token"], use_context=True)
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher

        # Commands
        self.utils = bot_utils.BotUtils(config, auth_chat_ids, self.bot)
        self.root = root.RootCommand(config, auth_chat_ids, self.utils)
        self.settings = settings.SettingsCommand(config, auth_chat_ids, self.utils)
        self.snapshot = snapshot.SnapshotCommand(config, auth_chat_ids, self.utils)

        # FSM
        self.settings_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.settings.toggle, pattern='^' + str(bot_events.TOGGLE_CLICK) + '$'),
                          CallbackQueryHandler(self.settings.get_log, pattern='^' + str(bot_events.LOG_CLICK) + '$'),
                          CallbackQueryHandler(self.settings.face_number,
                                               pattern='^' + str(bot_events.FACES_CLICK) + '$'),
                          CallbackQueryHandler(self.settings.seconds_to_analyze,
                                               pattern='^' + str(bot_events.SECONDS_CLICK) + '$'),
                          CallbackQueryHandler(self.settings.frame_percentage,
                                               pattern='^' + str(bot_events.PERCENTAGE_CLICK) + '$'),
                          ],
            states={
                bot_states.RESP_SETTINGS: [
                    CallbackQueryHandler(self.settings.setting_resp,
                                         pattern="^(?!" + str(bot_events.BACK_CLICK) + ").*")]
            },
            fallbacks=[CallbackQueryHandler(self.root.exit, pattern='^' + str(bot_events.EXIT_CLICK) + '$'),
                       CallbackQueryHandler(self.settings.show_settings,
                                            pattern='^' + str(bot_events.BACK_CLICK) + '$')],
            per_message=True,
            map_to_parent={
                bot_states.END: bot_states.LOGGED,
                bot_states.SETTINGS: bot_states.SETTINGS
            }
        )

        # Level 1 only callback (no warning)
        self.menu_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.settings.show_settings, pattern='^' + str(bot_events.SETTINGS_CLICK) + '$'),
            ],
            states={
                bot_states.SETTINGS: [self.settings_handler]
            },
            fallbacks=[CallbackQueryHandler(self.root.exit, pattern='^' + str(bot_events.EXIT_CLICK) + '$')],
            per_message=True,
            map_to_parent={
                bot_states.END: bot_states.LOGGED,
                bot_states.LOGGED: bot_states.LOGGED,
                bot_states.NOT_LOGGED: bot_states.NOT_LOGGED
            }
        )

        self.snapshot_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.snapshot.snapshot_resp, pattern="^(?!" + str(bot_events.EXIT_CLICK) + ").*")],
            states={},
            fallbacks=[CallbackQueryHandler(self.root.exit, pattern='^' + str(bot_events.EXIT_CLICK) + '$')],
            per_message=True,
            map_to_parent={
                bot_states.LOGGED: bot_states.LOGGED,
                bot_states.NOT_LOGGED: bot_states.NOT_LOGGED
            }
        )

        # Level 0
        self.conversationHandler = ConversationHandler(
            entry_points=[CommandHandler('start', callback=self.root.start)],
            states={
                bot_states.NOT_LOGGED: [CommandHandler('start', callback=self.root.start)],
                bot_states.LOGGED: [CommandHandler('menu', callback=self.root.show_logged_menu),
                                    CommandHandler('snapshot', callback=self.snapshot.show_snapshot),
                                    self.menu_handler, self.snapshot_handler],
            },
            fallbacks=[CallbackQueryHandler(self.root.exit, pattern='^' + str(bot_events.EXIT_CLICK) + '$')]
        )
        # Init handlers
        self.dispatcher.add_handler(self.conversationHandler)

    def start_web_hook(self):
        # START WEBHOOK
        network = self.config["network"]["telegram"]
        key = utils.get_project_relative_path(network["key"])
        cert = utils.get_project_relative_path(network["cert"])
        utils.start_web_hook(self.updater, self.config["token"], network["ip"], network["port"], key, cert)
        logger.info("Started Webhook bot")

    def start_polling(self):
        logger.info("Started Polling bot")
        self.updater.start_polling()

    def get_bot(self):
        return self.bot
