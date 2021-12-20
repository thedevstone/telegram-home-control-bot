import logging
import os
from typing import Dict

import requests
from requests import Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, File
from telegram import Update
from telegram.ext import CallbackContext

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils
from cameras.camera import Camera

logger = logging.getLogger(os.path.basename(__file__))


class SpeakCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, camera_instances: Dict[str, Camera], conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.camera_instances: Dict[str, Camera] = camera_instances
        self.utils = conversation_utils

    def select_camera(self, update: Update, _):
        kb = []
        for camera in self.auth_chat_ids[update.effective_chat.id]["cameras"]:
            kb.append([InlineKeyboardButton("{}".format(camera), callback_data="{}".format(camera))])
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="Select camera:", reply_markup=reply_markup)
        return bot_states.SPEAK

    def speak_resp(self, update: Update, context: CallbackContext):
        update.callback_query.answer()
        cam_name = update.callback_query.data
        context.user_data["selected_camera"] = cam_name
        message = update.callback_query.edit_message_text("Send a text or audio | type 'exit' to exit")
        self.utils.check_last_and_delete(update, context, message)
        return bot_states.SPEAK_MESSAGE

    def speak_message(self, update: Update, context: CallbackContext):
        cam_name = context.user_data["selected_camera"]
        if update.message.text:
            message = update.message.text.lower().encode("utf-8")
            if message == b"exit":
                update.effective_message.delete()
                return bot_states.LOGGED
            try:
                response: Response = self.camera_instances[cam_name].speak(message)
                message = update.effective_message.reply_text(text=response.json()["description"])
                self.utils.check_last_and_delete(update, context, message)
            except requests.exceptions.Timeout:
                logger.error("Timeout")
                message = update.effective_message.reply_text(text="Timeout")
                self.utils.check_last_and_delete(update, context, message)
                return bot_states.LOGGED
            update.effective_message.delete()
        return bot_states.SPEAK_MESSAGE
