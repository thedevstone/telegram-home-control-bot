import logging
import os
from io import BytesIO

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from bot.conversation.fsm import bot_states, bot_events
from bot.conversation.video import video_utils
from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class VideoCommand(object):
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
        return bot_states.VIDEO

    def video_resp(self, update: Update, context: CallbackContext):
        cam_name = update.callback_query.data
        context.user_data["cam_name"] = cam_name
        update.callback_query.answer()
        # Video times
        ip = self.config["cameras"][cam_name]["ip-port"]
        video_times = video_utils.get_last_folder_video_times(ip)
        # Add all rows with 3 times
        elem_per_row = 3
        rows = int(len(video_times) / elem_per_row)
        kb = [[InlineKeyboardButton("{}".format(video_times[i * elem_per_row + n]),
                                    callback_data="{}-{}".format(i * elem_per_row + n,
                                                                 video_times[i * elem_per_row * n]))
               for n in range(elem_per_row)] for i in range(rows)]
        # Add last row with remaining times
        remain_in_last_row = int(len(video_times) % elem_per_row)
        start_idx = len(video_times) - remain_in_last_row
        kb.append([InlineKeyboardButton("{}".format(video_times[start_idx + i]),
                                        callback_data="{}-{}".format(start_idx + i, video_times[start_idx + i])) for i
                   in range(remain_in_last_row)])
        # Add last button
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="Get video:", reply_markup=reply_markup)
        return bot_states.VIDEO_OLDNESS

    def video_oldness(self, update: Update, context: CallbackContext):
        oldness_time = update.callback_query.data.split("-")
        oldness = oldness_time[0]
        time = oldness_time[1]
        update.callback_query.answer()
        # Camera web service
        cam_name = context.user_data["cam_name"]
        ip = self.config["cameras"][cam_name]["ip-port"]
        camera_type = self.config["cameras"][cam_name]["type"]
        video_url = self.config["camera-types"][camera_type]["web-services"]["video"]
        update.callback_query.answer()
        try:
            response = requests.get("http://{}{}?oldness={}&type=4".format(ip, video_url, oldness), timeout=20)
            update.effective_message.reply_video(video=BytesIO(response.content),
                                                 caption="{}: video-[{}]".format(cam_name, time))
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
