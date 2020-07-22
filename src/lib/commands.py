import os
import logging
from telegram import Bot, ParseMode, ForceReply, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InputTextMessageContent, Update
from lib import botUtils
import yaml
import numpy as np
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

log = logging.getLogger(os.path.basename(__file__))
CREDENTIALS, LOGGED, SETTINGS = range(3)
SETTINGS_RESP, END = range(3, 5)

# Different constants for this example
LOG, FACES, SECONDS, PERCENTAGE, EXIT  = range(10, 15)
START_OVER = range(15, 16)

class Command(object):
    # Constructor
    def __init__(self, config, authChatIds):
        self.config = config
        self.authChatIds = authChatIds

    #STATE=START
    def start(self, update, context):
        chat_id = update.effective_chat.id
        username = update.effective_user["username"]
        #Init user if not exists
        if (not self.chatExists(chat_id)):
            self.init_user(chat_id, username)
        # Store value
        if (self.authChatIds[chat_id]["logged"] == True):
            update.callback_query.answer()
            update.callback_query.edit_message_text(text="You are already logged in!", reply_markup=None)
            return LOGGED
        else:
            context.bot.send_message(chat_id,text="Welcome to *Home Control Bot* by *NiNi* [link](http://google.com)\.", parse_mode=ParseMode.MARKDOWN_V2)
            update.message.reply_text(text="Send me bot credentials: <username>:<password>", reply_markup=None)
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


        #Credentials ok
        if (username == splitted[0] and password == splitted[1]):
            self.authChatIds[chat_id]["logged"] = True
            context.bot.send_message(chat_id, text = "Autentication succeded")
            log.info("New user logged: {} chat_id: {}".format(username_telegram, chat_id))
            self.logAdmin("New user logged: {} chat_id: {}".format(username_telegram, chat_id), context)
            return LOGGED
        else: #Credentials not ok
            self.authChatIds[chat_id]["logged"] = False
            if (self.authChatIds[chat_id]["tries"] >= users_conf["max_tries"]):
                self.authChatIds[chat_id]["banned"] = True
            else: 
                self.authChatIds[chat_id]["tries"] = self.authChatIds[chat_id]["tries"] + 1
            #User banned
            if (self.authChatIds[chat_id]["banned"] == True):
                context.bot.send_message(chat_id, text = "You are banned. Bye Bye")
                log.warn("User: {} banned with chat_id: {}".format(username, chat_id))
                self.logAdmin("User: {} banned with chat_id: {}".format(username, chat_id), context)
                return ConversationHandler.END
            else:
                context.bot.send_message(chat_id, text = "Autentication failed.\nSend me your credentials again: <username>:<password>")
                log.warn("New user: {} try autenticate with chat_id: {}".format(username_telegram, chat_id))
                self.logAdmin("New user: {} try autenticate with chat_id: {}".format(username_telegram, chat_id), context)
            return CREDENTIALS

    def show_settings(self, update, context):
        keyboard = [[InlineKeyboardButton(text="GetLog", callback_data=LOG)],
                    [InlineKeyboardButton(text="Number of Faces", callback_data=FACES)],
                    [InlineKeyboardButton(text="Seconds to analyze", callback_data=SECONDS)],
                    [InlineKeyboardButton(text="Sampling frame percentage", callback_data=PERCENTAGE)],
                    [InlineKeyboardButton(text="❌", callback_data=EXIT)]
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text = "Select setting:", reply_markup=reply_markup)
        return SETTINGS

    def settings(self, update, context):
        setting = int(update.callback_query.data)
        keyboard = None
        text = ""
        state = SETTINGS_RESP
        
        update.callback_query.answer()
        username_telegram = update.effective_user
        if (self.isAdmin(username_telegram)):
            text = "You are not admin!"
        
        if (setting == LOG):
            text = self.getLog()
            state = END
        elif (setting == FACES):
            text = "Insert the number of faces to detect [{}]".format(self.config["analysis"]["faces"])
            keyboard = self.face_number()
        elif (setting == SECONDS):
            text = "Insert the number of seconds to analyze [{}] (low is faster)".format(self.config["analysis"]["seconds"])
            keyboard = self.seconds_to_analyze()
        elif (setting == PERCENTAGE):
            text = "Insert the percentage of frame to analyze [{}] (low is faster)".format(self.config["analysis"]["sampling_percentage"])
            keyboard = self.frame_percentage()
        elif (setting == EXIT):
            update.callback_query.edit_message_reply_markup(None)
            self.start(update, context)
            return END
        
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        return state

    def setting_resp(self, update: Update, context):
        setting = update.callback_query.data
        text = ""
        data = setting.split(":")
        command = data[0]
        value = data[1]
        
        if (command == "face"):
            faces = int(value)
            self.config["analysis"]["faces"] = faces
            text = "The system will analyze {}s videos".format(faces)
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

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)
        return END

    def getLog(self):
        with open(botUtils.getProjectRelativePath("app.log")) as f:
            return f.readlines()

    def face_number(self):
        kb = [[InlineKeyboardButton(n, callback_data="face:{}".format(n)) for n in range(0, 5)]]
        kb_markup = InlineKeyboardMarkup(kb)
        return kb_markup

    def seconds_to_analyze(self):
        elem_per_row, row_number, step = 10, 2, 2
        kb = [[InlineKeyboardButton(x, callback_data="seconds:{}".format(x)) for x in range(y * elem_per_row + step, y * elem_per_row + elem_per_row + step , step)] for y in range(0, row_number)]
        kb_markup = InlineKeyboardMarkup(kb)
        return kb_markup
    
    def frame_percentage(self):
        kb = [[InlineKeyboardButton(round(n, 1), callback_data="percentage:{}".format(n)) for n in np.linspace(0.1, 0.5, 5)]]
        kb_markup = InlineKeyboardMarkup(kb)
        return kb_markup


    #STATE=LOGGED
    def logout(self, update, context):
        chat_id = update.effective_chat.id
        self.authChatIds[chat_id]["logged"] = False
        context.bot.send_message(chat_id, text = "Logged out")
        return ConversationHandler.END

    def cancel(self, update):
        print("cancel")
        return ConversationHandler.END

    def error(self, update, error):
        """Log Errors caused by Updates."""
        log.warning('Update "%s" caused error "%s"', update, update.error)

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
