import logging
import os
from io import BytesIO
from typing import Dict

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils
from cameras.camera import Camera
from cameras.unsupported_operation_error import UnsupportedOperationError

logger = logging.getLogger(os.path.basename(__file__))


class SnapshotCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, camera_instances: Dict[str, Camera], conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.camera_instances: Dict[str, Camera] = camera_instances
        self.utils = conversation_utils

    def select_camera(self, update: Update, _):
        kb = []
        for camera in (self.auth_chat_ids[update.effective_chat.id]["cameras"] or []):
            kb.append([InlineKeyboardButton("{}".format(camera), callback_data="{}".format(camera))])
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="Select camera:", reply_markup=reply_markup)
        return bot_states.SNAPSHOT

    def snapshot_resp(self, update: Update, context):
        cam_name = update.callback_query.data
        update.callback_query.answer()
        try:
            response: bytes = self.camera_instances[cam_name].get_snapshot()
            update.effective_message.reply_photo(BytesIO(response), caption=cam_name + ": shapshot")
        except UnsupportedOperationError as e:
            logger.error(str(e))
            message = update.effective_message.reply_text(text=str(e))
            self.utils.check_last_and_delete(update, context, message)
            return bot_states.LOGGED
        except requests.exceptions.Timeout:
            logger.error("Timeout")
            message = update.effective_message.reply_text(text="Timeout")
            self.utils.check_last_and_delete(update, context, message)
            return bot_states.LOGGED
        except telegram.error.BadRequest:
            logger.error("Bad request")
            message = update.effective_message.reply_text(text="Empty file")
            self.utils.check_last_and_delete(update, context, message)
            return bot_states.LOGGED
        update.effective_message.delete()
        return bot_states.LOGGED
