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
from switches.switch import Switch

logger = logging.getLogger(os.path.basename(__file__))


class SwitchCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, switch_instances: Dict[str, Switch], conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.switch_instances: Dict[str, Switch] = switch_instances
        self.utils = conversation_utils

    def select_switch(self, update: Update, _):
        kb = []
        for switch in (self.auth_chat_ids[update.effective_chat.id]["switches"] or []):
            kb.append([InlineKeyboardButton("{}".format(switch), callback_data="{}".format(switch))])
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="Select switch:", reply_markup=reply_markup)
        return bot_states.SWITCH

    def switch_resp(self, update: Update, context: CallbackContext):
        update.callback_query.answer()
        switch_name = update.callback_query.data
        context.user_data["selected_switch"] = switch_name
        self.switch_instances[switch_name].inpulse()
        update.effective_message.delete()
        return bot_states.LOGGED
