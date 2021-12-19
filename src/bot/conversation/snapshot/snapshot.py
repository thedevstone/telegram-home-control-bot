import logging
import os
from io import BytesIO

import requests
import telegram
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

    def select_camera(self, update: Update, _):
        kb = []
        for camera in self.auth_chat_ids[update.effective_chat.id]["cameras"]:
            kb.append([InlineKeyboardButton("{}".format(camera), callback_data="{}".format(camera))])
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="Select camera:", reply_markup=reply_markup)
        return bot_states.SNAPSHOT

    def snapshot_resp(self, update: Update, context):
        cam_name = update.callback_query.data
        ip = self.config["cameras"][cam_name]["ip"]
        port = self.config["cameras"][cam_name]["port"]
        username = self.config["cameras"][cam_name]["username"]
        password = self.config["cameras"][cam_name]["password"]
        camera_type = self.config["cameras"][cam_name]["type"]
        snapshot_url = self.config["camera-types"][camera_type]["web-services"]["snapshot"]
        update.callback_query.answer()
        try:
            response = requests.get(
                "http://{}:{}{}&username={}&password={}".format(ip, port, snapshot_url, username, password), timeout=10)
            update.effective_message.reply_photo(BytesIO(response.content), caption=cam_name + ": shapshot")
        except requests.exceptions.Timeout:
            logger.error("Timeout")
            message = update.effective_message.reply_text(text="Timeout")
            self.utils.check_last_and_delete(update, context, message)
        except telegram.error.BadRequest:
            logger.error("Bad request")
            message = update.effective_message.reply_text(text="Empty file")
            self.utils.check_last_and_delete(update, context, message)
        update.effective_message.delete()
        return bot_states.LOGGED
