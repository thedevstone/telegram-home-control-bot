import os
import logging
from telegram import Bot, ParseMode
from lib import botUtils
import yaml
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

log = logging.getLogger(os.path.basename(__file__))
CREDENTIALS, LOGGED, FACE_NUMBER = range(3)

class Command(object):
    # Constructor
    def __init__(self, config, authChatIds):
        self.config = config
        self.authChatIds = authChatIds

    #STATE=START
    def start(self, update, context):
        chat_id = update.effective_chat.id
        # Store value
        context.bot.send_message(chat_id,
                 text="Welcome to *Home Control Bot* by *NiNi* [link](http://google.com)\.", 
                 parse_mode=ParseMode.MARKDOWN_V2)
        if ('logged' not in context.user_data):
            context.bot.send_message(chat_id, text = "You are not logged in!\nSend me your credentials: <username>:<password>")
        elif (context.user_data["logged"] == True):
            context.bot.send_message(chat_id, text = "You are already logged in!")
        else: 
            context.bot.send_message(chat_id, text = "You are not logged in!\nSend me your credentials: <username>:<password>")
        return CREDENTIALS

    #STATE=CREDENTIALS
    def credentials(self, update, context):
        username_telegram = update.message.from_user["username"]
        chat_id = update.effective_chat.id
        credentials = self.config["credentials"]
        users_conf = self.config["users"]
        username = credentials["username"]
        password = credentials["password"]
        message = update.message.text
        splitted = message.split(':')
        #User always saved
        if (chat_id not in self.authChatIds):
            self.authChatIds[chat_id] = dict()
            self.authChatIds[chat_id]["username"] = username_telegram
            self.authChatIds[chat_id]["tries"] = 1
            self.authChatIds[chat_id]["logged"] = False
            self.authChatIds[chat_id]["banned"] = False
            self.authChatIds[chat_id]["admin"] = False

        elif (self.authChatIds[chat_id]["banned"] == True):
            context.bot.send_message(chat_id, text = "You are banned. Bye Bye")
            log.warn("User: {} banned with chat_id: {}".format(username, chat_id))
            self.logAdmin("User: {} banned with chat_id: {}".format(username, chat_id), context)
            return ConversationHandler.END

        if (username == splitted[0] and password == splitted[1]):
            context.user_data["logged"] = True
            self.authChatIds[chat_id]["logged"] = True
            self.authChatIds[chat_id]["banned"] = False

            context.bot.send_message(chat_id, text = "Autentication succeded")
            log.info("New user logged: {} chat_id: {}".format(username_telegram, chat_id))
            self.logAdmin("New user logged: {} chat_id: {}".format(username_telegram, chat_id), context)
            return LOGGED
        else:
            context.user_data["logged"] = False
            self.authChatIds[chat_id]["logged"] = False
            if (self.authChatIds[chat_id]["tries"] >= users_conf["max_tries"]):
                self.authChatIds[chat_id]["banned"] = True
            else: 
                self.authChatIds[chat_id]["tries"] = self.authChatIds[chat_id]["tries"] + 1

            context.bot.send_message(chat_id, text = "Autentication failed.\nSend me your credentials again: <username>:<password>")
            log.warn("New user: {} try autenticate with chat_id: {}".format(username_telegram, chat_id))
            self.logAdmin("New user: {} try autenticate with chat_id: {}".format(username_telegram, chat_id), context)
            return CREDENTIALS
        return CREDENTIALS

    #STATE=LOGGED
    def face_number(self, update, context):
        username_telegram = update.message.from_user["username"]
        chat_id = update.effective_chat.id
        if (isAdmin(username_telegram)):
            context.bot.send_message(chat_id, text = "Insert the number of faces:")
            return FACE_NUMBER
        else: 
            context.bot.send_message(chat_id, text = "You are not the admin")
            return LOGGED
        
    #STATE=FACE_NUMBER
    def set_face_number(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        try:
            faces = int(message)
            self.config["analysis"]["faces"] = faces
            context.bot.send_message(chat_id, text = "The system will detect {} faces".format(faces))
        except ValueError:
            context.bot.send_message(chat_id, text = "Insert the number of faces to detect")
        return FACE_NUMBER

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

    def isAdmin(self, username):
        return username == self.config["users"]["admin"]
            