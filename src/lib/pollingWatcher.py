import os
import glob
from lib import botUtils, videoAnalysis
import threading
import time
import matplotlib.pyplot as plt
import matplotlib
import cv2
import logging
import telegram
from PIL import Image
from io import BytesIO

class Watcher:
    def __init__(self, directory_to_watch, videoAnalysis, authChatIds, bot, config):
        self.directory_to_watch = directory_to_watch
        self.videoAnalysis = videoAnalysis
        self.authChatIds = authChatIds
        self.bot = bot
        self.config = config
        self.stop = False

    def checkFolder(self):
        while(True):
            time.sleep(1)
            newset = glob.glob(self.directory_to_watch + "/*.mp4")
            if len(newset) != 0:
                video = list(newset)[0]
                print("Received created event - ", video)
                try: 
                    self.processFile(video) 
                    os.remove(video)
                except: pass
    
    def processFile(self, file):
        faces = self.videoAnalysis.analyze(file)
        for face in faces:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            logged_users = dict((k, v) for k, v in self.authChatIds.items() if v["logged"] == True)
            for chatId, value in logged_users.items():
                temp_file = BytesIO()
                temp_file.name = 'temp.png'
                im = Image.fromarray(face)
                im.save(temp_file, format="png")
                temp_file.seek(0)
                self.bot.send_photo(chatId, temp_file)

if __name__ == "__main__":
    import botUtils
    import videoAnalysis
    videoAnalysis = videoAnalysis.VideoAnalysis()
    watcher = Watcher(".", videoAnalysis)
    watcher.checkFolder()