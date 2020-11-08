import logging
import os

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ConversationHandler

from lib import botStates, botEvents
from lib import botUtils

logger = logging.getLogger(os.path.basename(__file__))


class Command(object):
    # Constructor
    def __init__(self, config, auth_chat_ids):
        self.config = config
        self.auth_chat_ids = auth_chat_ids

    @staticmethod
    def check_last_and_delete(_, context, message):
        if "last_message" in context.user_data and message is not None:
            context.user_data["last_message"].delete()
            context.user_data["last_message"] = message
        elif "last_message" in context.user_data and message is None:
            context.user_data["last_message"].delete()
            del context.user_data["last_message"]
        elif "last_message" not in context.user_data and message is not None:
            context.user_data["last_message"] = message
        else:
            pass  # message not present or not passed

    # STATE=START
    def start(self, update, context):
        # return LOGGED
        chat_id = update.effective_chat.id
        username = update.effective_user["username"]
        # Init user if not exists
        if not self.chat_exists(chat_id):
            self.init_user(chat_id, username)
        # Store value
        if self.auth_chat_ids[chat_id]["logged"] is True:
            update.callback_query.answer()
            update.effective_message.delete()
            return botStates.LOGGED
        else:
            message = context.bot.send_message(chat_id,
                                               text="Welcome to *Home Control Bot* by *NiNi* [link]("
                                                    "https://github.com/Giulianini/yi-hack-control-bot)\nPlease "
                                                    "login",
                                               parse_mode=ParseMode.MARKDOWN_V2)
            self.check_last_and_delete(update, context, message)
            return botStates.NOT_LOGGED

    def login(self, update, context):
        message = update.message.reply_text(text="Send me bot credentials: <username>:<password>", reply_markup=None)
        self.check_last_and_delete(update, context, message)
        update.message.delete()
        return botStates.CREDENTIALS

    # STATE=CREDENTIALS
    def credentials(self, update, context):
        # User and chat id
        username_telegram = update.effective_user["username"]
        chat_id = update.effective_chat.id
        # Get config
        credentials = self.config["credentials"]
        users_conf = self.config["users"]
        username = credentials["username"]
        password = credentials["password"]
        message = update.message.text
        splitted = message.split(':')
        update.message.delete()

        # Credentials ok
        if username == splitted[0] and password == splitted[1] and self.auth_chat_ids[chat_id]["banned"] is False:
            self.auth_chat_ids[chat_id]["logged"] = True
            self.check_admin_logged()
            message_sent = context.bot.send_message(chat_id, text="✅ Authentication succeeded")
            self.check_last_and_delete(update, context, message_sent)
            logger.info("New user logged: {} chat_id: {}".format(username_telegram, chat_id))
            # self.logAdmin("New user logged: {} chat_id: {}".format(username_telegram, chat_id), context)
            return botStates.LOGGED
        else:  # Credentials not ok
            self.auth_chat_ids[chat_id]["logged"] = False
            if self.auth_chat_ids[chat_id]["tries"] >= users_conf["max_tries"]:
                self.auth_chat_ids[chat_id]["banned"] = True
            else:
                self.auth_chat_ids[chat_id]["tries"] = self.auth_chat_ids[chat_id]["tries"] + 1
            # User banned
            if self.auth_chat_ids[chat_id]["banned"] is True:
                message_sent = context.bot.send_message(chat_id, text="😢 You are banned. Bye Bye")
                self.check_last_and_delete(update, context, message_sent)
                logger.warning("User: {} banned with chat_id: {}".format(username, chat_id))
                # self.logAdmin("User: {} banned with chat_id: {}".format(username, chat_id), context)
                return ConversationHandler.END
            else:
                message_sent = context.bot.send_message(chat_id,
                                                        text="❌ Authentication failed.\nSend me your credentials "
                                                             "again: <username>:<password>")
                self.check_last_and_delete(update, context, message_sent)
                logger.warning("New user: {} try authenticate with chat_id: {}".format(username_telegram, chat_id))
            return botStates.CREDENTIALS

    def show_logged_menu(self, update, context):
        self.check_last_and_delete(update, context, None)
        update.message.delete()
        keyboard = [[InlineKeyboardButton(text="Settings", callback_data=str(botEvents.SETTINGS_CLICK))],
                    [InlineKeyboardButton(text="Logout", callback_data=str(botEvents.LOGOUT_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(botEvents.EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text="Menu", reply_markup=reply_markup)
        return botStates.LOGGED

    def show_settings(self, update: Update, context):
        update.callback_query.answer()
        username_telegram = update.effective_user["username"]
        status = self.config["analysis"]["status"]
        if not self.is_admin(username_telegram):
            message_sent = update.callback_query.edit_message_text(text="🔐 You are not an admin")
            self.check_last_and_delete(update, context, message_sent)
            return botStates.LOGGED
        keyboard = [[InlineKeyboardButton(text="Switch Off" if status else "Switch On",
                                          callback_data=str(botEvents.TOGGLE_CLICK))],
                    [InlineKeyboardButton(text="GetLog", callback_data=str(botEvents.LOG_CLICK))],
                    [InlineKeyboardButton(text="Number of Faces", callback_data=str(botEvents.FACES_CLICK))],
                    [InlineKeyboardButton(text="Seconds to analyze", callback_data=str(botEvents.SECONDS_CLICK))],
                    [InlineKeyboardButton(text="Analysis fps", callback_data=str(botEvents.PERCENTAGE_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(botEvents.EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text="Select setting:", reply_markup=reply_markup)
        return botStates.SETTINGS

    def logout(self, update: Update, context):
        update.callback_query.answer()
        chat_id = update.effective_chat.id
        self.auth_chat_ids[chat_id]["logged"] = False
        self.check_admin_logged()
        update.effective_message.delete()
        return self.start(update, context)

    @staticmethod
    def exit(update: Update):
        update.callback_query.answer()
        update.effective_message.delete()
        return botStates.END

    def toggle(self, update: Update):
        status = self.config["analysis"]["status"]
        self.config["analysis"]["status"] = not status
        update.callback_query.answer()
        # self.exit(update, context) and delete after
        kb = [[InlineKeyboardButton(text="❌", callback_data=str(
            botEvents.EXIT_CLICK))]]  # Exit if you want to exit Back to return to menu
        reply_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text="System switched Off" if status else "System switched On",
                                                reply_markup=reply_markup)
        return botStates.SETTINGS  # Same state for exit

    @staticmethod
    def get_log(update: Update):
        update.callback_query.answer()
        with open(botUtils.get_project_relative_path("app.log")) as f:
            keyboard = [[InlineKeyboardButton(text="❌", callback_data=str(botEvents.BACK_CLICK))]]
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
        return botStates.RESP_SETTINGS

    def face_number(self, update: Update):
        update.callback_query.answer()
        text = "Insert the number of faces to detect [{}]".format(self.config["analysis"]["faces"])
        kb = [[InlineKeyboardButton("{}".format(n), callback_data="face:{}".format(n)) for n in range(0, 6)],
              [InlineKeyboardButton(text="❌", callback_data=str(botEvents.BACK_CLICK))]]
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return botStates.RESP_SETTINGS

    def seconds_to_analyze(self, update: Update):
        update.callback_query.answer()
        text = "Insert the number of seconds to analyze [{}] (low is faster)".format(self.config["analysis"]["seconds"])
        elem_per_row, row_number, step = 60, 2, 10
        kb = [[InlineKeyboardButton("{}".format(x), callback_data="seconds:{}".format(x)) for x in
               range(y * elem_per_row + step, y * elem_per_row + elem_per_row + step, step)] for y in
              range(0, row_number)]
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(botEvents.BACK_CLICK))])
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return botStates.RESP_SETTINGS

    def frame_percentage(self, update: Update):
        update.callback_query.answer()
        anal_fps = self.config["analysis"]["anal_fps"]
        text = "Insert the analysis fps [{}] (low is faster)".format(anal_fps)
        kb = [[InlineKeyboardButton("{}".format(n), callback_data="anal_fps:{}".format(n)) for n in range(0, 10)],
              [InlineKeyboardButton(text="❌", callback_data=str(botEvents.BACK_CLICK))]]
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return botStates.RESP_SETTINGS

    def setting_resp(self, update: Update):
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
            [InlineKeyboardButton(text="❌", callback_data=str(botEvents.EXIT_CLICK))]]  # Exit if you want to exit
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return botStates.LOGGED

    def log_admin(self, msg, context):
        for k1, v1 in self.auth_chat_ids.items():
            if v1["username"] == self.config["users"]["admin"]:
                context.bot.send_message(k1, text=msg)

    def chat_exists(self, chat_id):
        return chat_id in self.auth_chat_ids

    def check_admin_logged(self):
        for k1, v1 in self.auth_chat_ids.items():
            if v1["logged"] is True and v1["admin"] is True:
                self.config["analysis"]["status"] = True
                return
        self.config["analysis"]["status"] = False

    def is_admin(self, username):
        return username == self.config["users"]["admin"]

    def init_user(self, chat_id, username):
        if chat_id not in self.auth_chat_ids:
            self.auth_chat_ids[chat_id] = dict()
            self.auth_chat_ids[chat_id]["username"] = username
            self.auth_chat_ids[chat_id]["tries"] = 1
            self.auth_chat_ids[chat_id]["logged"] = False
            self.auth_chat_ids[chat_id]["banned"] = False
            self.auth_chat_ids[chat_id]["admin"] = self.is_admin(username)
