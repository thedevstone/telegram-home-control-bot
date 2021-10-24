import logging
import os
from io import BytesIO

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class SnapshotCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.utils = conversation_utils

    def show_snapshot(self, update: Update, context):
        username_telegram = update.effective_user.username
        if not self.utils.is_admin(username_telegram):
            message_sent = update.callback_query.edit_message_text(text="🔐 You are not an admin")
            self.utils.check_last_and_delete(update, context, message_sent)
            return bot_states.LOGGED
        kb = []
        for key, value in self.config["network"]["cameras"].items():
            kb.append([InlineKeyboardButton("{}".format(key), callback_data="{}".format(key))])
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="Select camera:", reply_markup=reply_markup)
        return bot_states.SNAPSHOT

    def snapshot_resp(self, update: Update, _):
        cam_name = update.callback_query.data
        ip = self.config["network"]["cameras"][cam_name]["ip"]
        update.callback_query.answer()
        try:
            response = requests.get("http://{}/cgi-bin/snapshot.sh".format(ip), timeout=5)
            update.effective_message.reply_photo(BytesIO(response.content), caption=cam_name)
        except requests.exceptions.Timeout:
            pass
        update.effective_message.delete()
        return bot_states.LOGGED
