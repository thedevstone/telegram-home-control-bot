import os
import logging
from telegram import Bot, ParseMode
from lib import botUtils
import yaml
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters

log = logging.getLogger(os.path.basename(__file__))
CREDENTIALS, LOGGED, FACE_NUMBER, SECONDS, PERCENTAGE = range(5)

class Command(object):
    # Constructor
    def __init__(self, config, authChatIds):
        self.config = config
        self.authChatIds = authChatIds

    #STATE=START
    def start(self, update, context):
        chat_id = update.effective_chat.id
        username = update.message.from_user["username"]
        #Init user if not exists
        if (not self.chatExists(chat_id)):
            self.init_user(chat_id, username)
        # Store value
        context.bot.send_message(chat_id,text="Welcome to *Home Control Bot* by *NiNi* [link](http://google.com)\.", parse_mode=ParseMode.MARKDOWN_V2)
        if (self.authChatIds[chat_id]["logged"] == True):
            context.bot.send_message(chat_id, text = "You are already logged in!")
            return LOGGED
        else: 
            context.bot.send_message(chat_id, text = "Send me bot credentials: <username>:<password>")
            return CREDENTIALS

    #STATE=CREDENTIALS
    def credentials(self, update, context):
        #User and chatid
        username_telegram = update.message.from_user["username"]
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

    #STATE=LOGGED
    #Show keyboard
    def config_command(self, update, context, state, message):
        username_telegram = update.message.from_user["username"]
        chat_id = update.effective_chat.id
        if (self.isAdmin(username_telegram)):
            context.bot.send_message(chat_id, text = message)
            return state
        context.bot.send_message(chat_id, text = "You are not the admin")
        return LOGGED

    def face_number(self, update, context):
        return self.config_command(update, context, FACE_NUMBER, "Insert the number of faces to detect [{}]".format(self.config["analysis"]["faces"]))

    def seconds_to_analyze(self, update, context):
        return self.config_command(update, context, SECONDS, "Insert the number of seconds to analyze [{}] (low is faster)".format(self.config["analysis"]["seconds"]))
    
    def frame_percentage(self, update, context):
        return self.config_command(update, context, PERCENTAGE, "Insert the percentage of frame to analyze [{}] (low is faster)".format(self.config["analysis"]["sampling_percentage"]))

        
    #STATE=FACE_NUMBER
    def set_face_number(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        try:
            faces = int(message)
            self.config["analysis"]["faces"] = faces
            context.bot.send_message(chat_id, text = "The system will detect {} faces".format(faces))
            return LOGGED
        except ValueError:
            context.bot.send_message(chat_id, text = "Error! Insert the number of faces")
            return FACE_NUMBER

    def set_seconds_to_analyze(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        try:
            seconds = int(message)
            self.config["analysis"]["seconds"] = seconds
            context.bot.send_message(chat_id, text = "The system will analyze {}s videos".format(seconds))
            return LOGGED
        except ValueError:
            context.bot.send_message(chat_id, text = "Error! Insert the number of seconds")
            return SECONDS

    def set_frame_percentage(self, update, context):
        chat_id = update.effective_chat.id
        message = update.message.text
        try:
            perc = float(message)
            perc_int = perc * 100
            if (perc_int < 0 or perc_int > 100):
                context.bot.send_message(chat_id, text = "Error! Insert the percentage")
                return PERCENTAGE
            self.config["analysis"]["sampling_percentage"] = perc
            context.bot.send_message(chat_id, text = "The system will analyze {}/100 of frames".format(perc_int))
            return LOGGED
        except ValueError:
            context.bot.send_message(chat_id, text = "Error! Insert the number of percentage")
            return PERCENTAGE

    #STATE=LOGGED
    def logout(self, update, context):
        chat_id = update.effective_chat.id
        self.authChatIds[chat_id]["logged"] = False
        context.bot.send_message(chat_id, text = "Logged out")
        return ConversationHandler.END

    #STATE=LOGGED
    def getLog(self, update, context):
        chat_id = update.effective_chat.id
        with open(botUtils.getProjectRelativePath("app.log")) as f:
            content = f.readlines()
            context.bot.send_message(chat_id, text = content)
        return LOGGED

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