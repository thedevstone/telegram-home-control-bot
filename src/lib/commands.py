import os
import logging
from telegram import Bot, ParseMode, ForceReply, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InputTextMessageContent, Update
from lib import botUtils
import yaml
import numpy as np
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

log = logging.getLogger(os.path.basename(__file__))

## Level 1 STATES
# HANDLERS
CREDENTIALS, LOGGED, NOT_LOGGED, END = range(4)

SETTINGS, RESP_SETTINGS = range(4, 6)

# Selection Level 1 Menu
SETTINGS_CLICK, LOGOUT_CLICK, EXIT_CLICK, BACK_CLICK = map(chr, range(20, 24))

# Selection Level 2 Settings
LOG_CLICK, FACES_CLICK, SECONDS_CLICK, PERCENTAGE_CLICK  = map(chr, range(10, 14))

class Command(object):
    # Constructor
    def __init__(self, config, authChatIds):
        self.config = config
        self.authChatIds = authChatIds

    def check_last_and_delete(self, update, context, message):
        if ("last_message" in context.user_data and message != None):
            context.user_data["last_message"].delete()
            context.user_data["last_message"] = message
        elif ("last_message" in context.user_data and message == None):
            context.user_data["last_message"].delete()
            del context.user_data["last_message"]
        elif ("last_message" not in context.user_data and message != None):
            context.user_data["last_message"] = message
        else: pass # messaggio non c'è e non è stato passato

    #STATE=START
    def start(self, update, context):
        #return LOGGED
        chat_id = update.effective_chat.id
        username = update.effective_user["username"]
        #Init user if not exists
        if (not self.chatExists(chat_id)):
            self.init_user(chat_id, username)
        # Store value
        if (self.authChatIds[chat_id]["logged"] == True):
            update.callback_query.answer()
            update.effective_message.delete()
            return LOGGED
        else:
            message = context.bot.send_message(chat_id,text="Welcome to *Home Control Bot* by *NiNi* [link](https://github.com/Giulianini/yi-hack-control-bot)\.\nPlease login", parse_mode=ParseMode.MARKDOWN_V2)
            self.check_last_and_delete(update, context, message)
            return NOT_LOGGED

    def login(self, update, context):
        message = update.message.reply_text(text="Send me bot credentials: <username>:<password>", reply_markup=None)
        self.check_last_and_delete(update, context, message)
        update.message.delete()
        return CREDENTIALS

    #STATE=CREDENTIALS
    def credentials(self, update, context):
        #User and chatid
        username_telegram = update.effective_user["username"]
        chat_id = update.effective_chat.id
        #Get config
        credentials = self.config["credentials"]
        users_conf = self.config["users"]
        username = credentials["username"]
        password = credentials["password"]
        message = update.message.text
        splitted = message.split(':')
        update.message.delete()

        #Credentials ok
        if (username == splitted[0] and password == splitted[1] and self.authChatIds[chat_id]["banned"] == False):
            self.authChatIds[chat_id]["logged"] = True
            message_sent = context.bot.send_message(chat_id, text = "✅ Autentication succeded")
            self.check_last_and_delete(update, context, message_sent)
            log.info("New user logged: {} chat_id: {}".format(username_telegram, chat_id))
            #self.logAdmin("New user logged: {} chat_id: {}".format(username_telegram, chat_id), context)
            return LOGGED
        else: #Credentials not ok
            self.authChatIds[chat_id]["logged"] = False
            if (self.authChatIds[chat_id]["tries"] >= users_conf["max_tries"]):
                self.authChatIds[chat_id]["banned"] = True
            else: 
                self.authChatIds[chat_id]["tries"] = self.authChatIds[chat_id]["tries"] + 1
            #User banned
            if (self.authChatIds[chat_id]["banned"] == True):
                message_sent = context.bot.send_message(chat_id, text = "😢 You are banned. Bye Bye")
                self.check_last_and_delete(update, context, message_sent)
                log.warn("User: {} banned with chat_id: {}".format(username, chat_id))
                #self.logAdmin("User: {} banned with chat_id: {}".format(username, chat_id), context)
                return ConversationHandler.END
            else:
                message_sent = context.bot.send_message(chat_id, text = "❌ Authentication failed.\nSend me your credentials again: <username>:<password>")
                self.check_last_and_delete(update, context, message_sent)
                log.warn("New user: {} try autenticate with chat_id: {}".format(username_telegram, chat_id))
                #self.logAdmin("New user: {} try autenticate with chat_id: {}".format(username_telegram, chat_id), context)
            return CREDENTIALS

    def show_logged_menu(self, update, context):
        self.check_last_and_delete(update, context, None)
        update.message.delete()
        keyboard = [[InlineKeyboardButton(text="Settings", callback_data=str(SETTINGS_CLICK))],
                    [InlineKeyboardButton(text="Logout", callback_data=str(LOGOUT_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text = "Menu", reply_markup=reply_markup)
        return LOGGED

    def show_settings(self, update: Update, context):
        update.callback_query.answer()
        username_telegram = update.effective_user["username"]
        if (not self.isAdmin(username_telegram)):
            message_sent = update.callback_query.edit_message_text(text = "🔐 You are not an admin")
            self.check_last_and_delete(update, context, message_sent)
            return LOGGED
        keyboard = [[InlineKeyboardButton(text="GetLog", callback_data=str(LOG_CLICK))],
                    [InlineKeyboardButton(text="Number of Faces", callback_data=str(FACES_CLICK))],
                    [InlineKeyboardButton(text="Seconds to analyze", callback_data=str(SECONDS_CLICK))],
                    [InlineKeyboardButton(text="Sampling frame percentage", callback_data=str(PERCENTAGE_CLICK))],
                    [InlineKeyboardButton(text="❌", callback_data=str(EXIT_CLICK))]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text = "Select setting:", reply_markup=reply_markup)
        return SETTINGS

    def logout(self, update: Update, context):
        update.callback_query.answer()
        chat_id = update.effective_chat.id
        self.authChatIds[chat_id]["logged"] = False
        update.effective_message.delete()
        return self.start(update, context)

    def exit(self, update: Update, context):
        update.callback_query.answer()
        update.effective_message.delete()
        return END

    def get_log(self, update: Update, context):
        update.callback_query.answer()
        with open(botUtils.getProjectRelativePath("app.log")) as f:
            keyboard = [[InlineKeyboardButton(text="❌", callback_data=str(BACK_CLICK))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.callback_query.edit_message_text(text = f.readlines(), reply_markup=reply_markup)
        return RESP_SETTINGS
        
    def face_number(self, update: Update, context):
        update.callback_query.answer()
        text = "Insert the number of faces to detect [{}]".format(self.config["analysis"]["faces"])
        kb = [[InlineKeyboardButton(n, callback_data="face:{}".format(n)) for n in range(0, 5)],
            [InlineKeyboardButton(text="❌", callback_data=str(BACK_CLICK))]]
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return RESP_SETTINGS

    def seconds_to_analyze(self, update: Update, context):
        update.callback_query.answer()
        text = "Insert the number of seconds to analyze [{}] (low is faster)".format(self.config["analysis"]["seconds"])
        elem_per_row, row_number, step = 10, 2, 2
        kb = [[InlineKeyboardButton(x, callback_data="seconds:{}".format(x)) for x in range(y * elem_per_row + step, y * elem_per_row + elem_per_row + step , step)] for y in range(0, row_number)]
        kb.append([InlineKeyboardButton(text="❌", callback_data=str(BACK_CLICK))])
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return RESP_SETTINGS
    
    def frame_percentage(self, update: Update, context):
        update.callback_query.answer()
        text = "Insert the percentage of frame to analyze [{}] (low is faster)".format(self.config["analysis"]["sampling_percentage"])
        kb = [[InlineKeyboardButton(round(n, 1), callback_data="percentage:{}".format(n)) for n in np.linspace(0.1, 0.5, 5)],
            [InlineKeyboardButton(text="❌", callback_data=str(BACK_CLICK))]]
        kb_markup = InlineKeyboardMarkup(kb)
        update.callback_query.edit_message_text(text=text, reply_markup=kb_markup)
        return RESP_SETTINGS

    def setting_resp(self, update: Update, context):
        setting = update.callback_query.data
        text = ""
        data = setting.split(":")
        command = data[0]
        value = data[1]
        
        if (command == "face"):
            faces = int(value)
            self.config["analysis"]["faces"] = faces
            text = "The system will detect {} faces".format(faces)
            pass
        elif (command == "seconds"):
            seconds = int(value)
            self.config["analysis"]["seconds"] = seconds
            text = "The system will analyze {}s videos".format(seconds)
        elif (command == "percentage"):
            perc = float(value)
            perc_int = int(perc * 100)
            self.config["analysis"]["sampling_percentage"] = perc
            total_frames = self.config["analysis"]["seconds"] * self.config["analysis"]["fps"]
            analyzed_frames = int(total_frames * perc)
            text = "The system will analyze {} frames per video.\n({}% of all {} frames)".format(analyzed_frames, perc_int, total_frames)
            pass

        keyboard = [[InlineKeyboardButton(text="❌", callback_data=str(BACK_CLICK))]] #Exit if you want to exit
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.callback_query.answer()
        update.callback_query.edit_message_text(text = text, reply_markup=reply_markup)
        return LOGGED

    def logAdmin(self, msg, context):
        for k1,v1 in self.authChatIds.items():
            if (v1["username"] == self.config["users"]["admin"]):
                context.bot.send_message(k1, text = msg)

    def chatExists(self, chat_id):
        return chat_id in self.authChatIds

    def isAdmin(self, username):
        return username == self.config["users"]["admin"]
    
    def init_user(self, chat_id, username):
        if (chat_id not in self.authChatIds):
            self.authChatIds[chat_id] = dict()
            self.authChatIds[chat_id]["username"] = username
            self.authChatIds[chat_id]["tries"] = 1
            self.authChatIds[chat_id]["logged"] = False
            self.authChatIds[chat_id]["banned"] = False
            self.authChatIds[chat_id]["admin"] = self.isAdmin(username)
