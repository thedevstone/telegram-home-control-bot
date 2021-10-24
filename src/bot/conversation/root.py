import logging
import os

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class RootCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.utils = conversation_utils

    # STATE=START
    def start(self, update: Update, context):
        chat_id = update.effective_chat.id
        user = update.effective_user
        # Store value
        text = "Welcome to *Home Control Bot* by *NiNi* [link](https://github.com/Giulianini/yi-hack-control-bot)\n"
        if not self.utils.is_allowed(user.username):
            text = text + "🚫 User not allowed 🚫"
            message = context.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
            self.utils.check_last_and_delete(update, context, message)
            log_msg = "{} ({} {}) denied.".format(user.username, user.first_name, user.last_name)
            logger.warning(log_msg)
            self.utils.log_admin(log_msg, update, context)
            return bot_states.NOT_LOGGED
        # Init user if not exists
        self.utils.init_user(chat_id, user.username)
        log_msg = "{} ({} {}) active.".format(user.username, user.first_name, user.last_name)
        logger.warning(log_msg)
        self.utils.log_admin(log_msg, update, context)
        message = context.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        self.utils.check_last_and_delete(update, context, message)
        return bot_states.LOGGED

    def mqtt_switch(self, update: Update, context):
        if not self.utils.is_admin(update.effective_user.username):
            message_sent = update.callback_query.edit_message_text(text="🔐 You are not an admin")
            self.utils.check_last_and_delete(update, context, message_sent)
            return bot_states.LOGGED
        will_be_enabled = not self.config["mqtt"]["enable"]
        self.config["mqtt"]["enable"] = will_be_enabled
        message = update.callback_query.edit_message_text(
            text="MQTT is" + (" enabled" if will_be_enabled else " disabled"))
        self.utils.check_last_and_delete(update, context, message)

    def show_logged_menu(self, update, context):
        self.utils.check_last_and_delete(update, context, None)
        update.message.delete()
        mqtt_label = ("Enable" if not self.config["mqtt"]["enable"] else "Disable") + " MQTT"
        keyboard = [[InlineKeyboardButton(text=mqtt_label, callback_data=str(bot_events.MQTT_SWITCH_CLICK))],
                    [InlineKeyboardButton(text="Snapshot", callback_data=str(bot_events.SNAPSHOT_CLICK))],
                    [InlineKeyboardButton(text="Video", callback_data=str(bot_events.VIDEO_CLICK))],
                    [InlineKeyboardButton(text="Speak", callback_data=str(bot_events.SPEAK_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text="Menu", reply_markup=reply_markup)
        return bot_states.LOGGED

    @staticmethod
    def exit(update: Update, _):
        update.callback_query.answer()
        update.effective_message.delete()
        return bot_states.LOGGED
