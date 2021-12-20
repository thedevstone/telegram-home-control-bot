import logging
import os
from io import BytesIO
from typing import Dict

import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from bot.conversation.fsm import bot_states, bot_events
from bot.conversation.video import video_utils
from bot.utils.bot_utils import BotUtils
from cameras.camera import Camera
from cameras.unsupported_operation_error import UnsupportedOperationError

logger = logging.getLogger(os.path.basename(__file__))


class VideoCommand(object):
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
        return bot_states.VIDEO

    def video_resp(self, update: Update, context: CallbackContext):
        cam_name = update.callback_query.data
        context.user_data["cam_name"] = cam_name
        update.callback_query.answer()
        # Video times
        try:
            video_times = self.camera_instances[cam_name].get_video_times()
            logger.info(video_times)
            # USE VIDEO TIMES
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
                                            callback_data="{}-{}".format(start_idx + i, video_times[start_idx + i]))
                       for i in range(remain_in_last_row)])
            # Add last button
            kb.append([InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))])
            reply_markup = InlineKeyboardMarkup(kb)
            update.callback_query.edit_message_text(text="Get video:", reply_markup=reply_markup)
            return bot_states.VIDEO_OLDNESS
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

    def video_oldness(self, update: Update, context: CallbackContext):
        oldness_time = update.callback_query.data.split("-")
        oldness = oldness_time[0]
        time = oldness_time[1]
        update.callback_query.answer()
        # Camera web service
        cam_name = context.user_data["cam_name"]
        update.callback_query.answer()
        try:
            response = self.camera_instances[cam_name].get_video(int(oldness))
            update.effective_message.reply_video(video=BytesIO(response.content),
                                                 caption="{}: video-[{}]".format(cam_name, time))
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
