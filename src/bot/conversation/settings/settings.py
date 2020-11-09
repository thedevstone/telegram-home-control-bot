import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from bot.conversation.fsm import bot_states, bot_events
from bot.utils.bot_utils import BotUtils
from utils import utils

logger = logging.getLogger(os.path.basename(__file__))


class SettingsCommand(object):
    # Constructor
    def __init__(self, config, auth_chat_ids, conversation_utils: BotUtils):
        self.config = config
        self.auth_chat_ids = auth_chat_ids
        self.utils = conversation_utils

    def show_settings(self, update: Update, context):
        update.callback_query.answer()
        username_telegram = update.effective_user["username"]
        status = self.config["analysis"]["status"]
        if not self.utils.is_admin(username_telegram):
            message_sent = update.callback_query.edit_message_text(text="🔐 You are not an admin")
            self.utils.check_last_and_delete(update, context, message_sent)
            return bot_states.LOGGED
        keyboard = [[InlineKeyboardButton(text="Switch Off" if status else "Switch On",
                                          callback_data=str(bot_events.TOGGLE_CLICK))],
                    [InlineKeyboardButton(text="GetLog", callback_data=str(bot_events.LOG_CLICK))],
                    [InlineKeyboardButton(text="Number of Faces", callback_data=str(bot_events.FACES_CLICK))],
                    [InlineKeyboardButton(text="Seconds to analyze", callback_data=str(bot_events.SECONDS_CLICK))],
                    [InlineKeyboardButton(text="Analysis fps", callback_data=str(bot_events.PERCENTAGE_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text="Select setting:", reply_markup=reply_markup)
        return bot_states.SETTINGS

    def toggle(self, update: Update, _):
        status = self.config["analysis"]["status"]
        self.config["analysis"]["status"] = not status
        update.callback_query.answer()
        kb = [[InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))]]  # Back to return to menu
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="System switched Off" if status else "System switched On",
                                                reply_markup=reply_markup)
        return bot_states.SETTINGS  # Same state for exit

    @staticmethod
    def get_log(update: Update, _):
        update.callback_query.answer()
        with open(utils.get_project_relative_path("app.log")) as f:
            keyboard = [[InlineKeyboardButton(text="⬅️", callback_data=str(bot_events.BACK_CLICK))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = f.readlines()
            size = 0
            line_index = 0
            for line in reversed(text):
                line_len = len(line)
                if size + line_len < 4096:
                    size += line_len
                    line_index += 1

            text = text[-line_index:]
            long_text = ""
            for line in text:
                long_text += line + "\n"
            update.callback_query.edit_message_text(text=long_text, reply_markup=reply_markup)
        return bot_states.RESP_SETTINGS

    def face_number(self, update: Update, _):
        update.callback_query.answer()
        text = "Insert the number of faces to detect [{}]".format(self.config["analysis"]["faces"])
        kb = [[InlineKeyboardButton("{}".format(n), callback_data="face:{}".format(n)) for n in range(0, 6)],
              [InlineKeyboardButton(text="⬅️", callback_data=str(bot_events.BACK_CLICK))]]
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return bot_states.RESP_SETTINGS

    def seconds_to_analyze(self, update: Update, _):
        update.callback_query.answer()
        text = "Insert the number of seconds to analyze [{}] (low is faster)".format(self.config["analysis"]["seconds"])
        elem_per_row, row_number, step = 60, 2, 10
        kb = [[InlineKeyboardButton("{}".format(x), callback_data="seconds:{}".format(x)) for x in
               range(y * elem_per_row + step, y * elem_per_row + elem_per_row + step, step)] for y in
              range(0, row_number)]
        kb.append([InlineKeyboardButton(text="⬅️", callback_data=str(bot_events.BACK_CLICK))])
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return bot_states.RESP_SETTINGS

    def frame_percentage(self, update: Update, _):
        update.callback_query.answer()
        anal_fps = self.config["analysis"]["anal_fps"]
        text = "Insert the analysis fps [{}] (low is faster)".format(anal_fps)
        kb = [[InlineKeyboardButton("{}".format(n), callback_data="anal_fps:{}".format(n)) for n in range(0, 10)],
              [InlineKeyboardButton(text="⬅️", callback_data=str(bot_events.BACK_CLICK))]]
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return bot_states.RESP_SETTINGS

    def setting_resp(self, update: Update, _):
        setting = update.callback_query.data
        text = ""
        data = setting.split(":")
        command = data[0]
        value = data[1]

        if command == "face":
            faces = int(value)
            self.config["analysis"]["faces"] = faces
            text = "The system will detect {} faces".format(faces)
            pass
        elif command == "seconds":
            seconds = int(value)
            self.config["analysis"]["seconds"] = seconds
            text = "The system will analyze {}s videos".format(seconds)
        elif command == "anal_fps":
            anal_fps = int(value)
            self.config["analysis"]["anal_fps"] = anal_fps
            total_frames = self.config["analysis"]["seconds"] * anal_fps
            text = "The system will analyze at {} fps.\n({} frames will be analyzed)".format(anal_fps, total_frames)
            pass

        keyboard = [
            [InlineKeyboardButton(text="❌", callback_data=str(bot_events.EXIT_CLICK))]]  # Exit if you want to exit
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return bot_states.LOGGED
