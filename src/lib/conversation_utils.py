import logging
import os

from telegram import Update

logger = logging.getLogger(os.path.basename(__file__))


class ConversationUtils:
    def __init__(self, config, auth_chat_ids):
        # Constructor
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

    def is_admin(self, username):
        return username == self.config["users"]["admin"]

    def log_admin(self, msg, update: Update, context):
        if not self.is_admin(update.effective_user.username):
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
