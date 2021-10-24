import logging
import os
import subprocess

import requests
from requests import Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, File
from telegram import Update
from telegram.ext import CallbackContext

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class SpeakCommand(object):
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
        ip = self.config["cameras"][cam_name]["ip"]
        if update.message.text:
            message = update.message.text.lower().encode("utf-8")
            if message == b"exit":
                update.effective_message.delete()
                return bot_states.LOGGED
            try:
                response: Response = requests.post("http://{}:80/cgi-bin/speak.sh?lang=it-IT".format(ip), timeout=20,
                                                   data=message)
                message = update.effective_message.reply_text(
                    text="Error " + response.json()["description"] if response.json()["error"] else "Success")
                self.utils.check_last_and_delete(update, context, message)
            except requests.exceptions.Timeout:
                logger.error("Timeout")
                message = update.effective_message.reply_text(text="Timeout")
                self.utils.check_last_and_delete(update, context, message)
            update.effective_message.delete()
        else:
            file_info: File = context.bot.get_file(update.message.voice.file_id)
            file_info.download("voice.ogg")
            try:
                process = subprocess.run(
                    ['ffmpeg', '-i', "voice.ogg", "-ac", "1", "-ar", "16000", "-acodec", "pcm_s16le", "-v", "error",
                     "-y", "voice.wav"])
                if process.returncode != 0:
                    message = update.effective_message.reply_text(text="Error running ffmpeg process")
                    self.utils.check_last_and_delete(update, context, message)
                    return bot_states.SPEAK_MESSAGE
            except FileNotFoundError:
                message = update.effective_message.reply_text(text="Cannot find ffmpeg process")
                self.utils.check_last_and_delete(update, context, message)
                return bot_states.SPEAK_MESSAGE
            try:
                with open("voice.wav", "rb") as f:
                    requests.post("http://{}:80/cgi-bin/speaker.sh".format(ip), timeout=20, data=f.read(),
                                  headers={'Content-Type': 'application/octet-stream'})
            except requests.exceptions.Timeout:
                logger.error("Timeout")
                message = update.effective_message.reply_text(text="Timeout")
                self.utils.check_last_and_delete(update, context, message)
            update.effective_message.delete()
        return bot_states.SPEAK_MESSAGE
