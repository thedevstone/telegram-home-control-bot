import logging
import os

from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram.ext import Updater

from bot.conversation import root
from bot.conversation.fsm import bot_states, bot_events
from bot.conversation.settings import settings
from bot.conversation.snapshot import snapshot
from bot.conversation.video import video
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
        self.video = video.VideoCommand(config, auth_chat_ids, self.utils)

        # Level 1 only callback (no warning)
        self.menu_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.snapshot.show_snapshot, pattern='^' + str(bot_events.SNAPSHOT_CLICK) + '$'),
                CallbackQueryHandler(self.video.show_video, pattern='^' + str(bot_events.VIDEO_CLICK) + '$'),
            ],
            states={
                bot_states.SNAPSHOT: [CallbackQueryHandler(self.snapshot.snapshot_resp,
                                                           pattern="^(?!" + str(bot_events.EXIT_CLICK) + ").*")],
                bot_states.VIDEO: [CallbackQueryHandler(self.video.video_resp,
                                                        pattern="^(?!" + str(bot_events.EXIT_CLICK) + ").*")]
            },
            fallbacks=[CallbackQueryHandler(self.root.exit, pattern='^' + str(bot_events.EXIT_CLICK) + '$')],
            per_message=True,
            map_to_parent={
                bot_states.END: bot_states.LOGGED,
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
                                    self.menu_handler],
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
