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
    def __init__(self, directory_to_watch, videoAnalysis, authChatIds, bot):
        self.directory_to_watch = directory_to_watch
        self.videoAnalysis = videoAnalysis
        self.authChatIds = authChatIds
        self.bot = bot
        #self.savedSet = glob.glob(self.directory_to_watch + "/*.mp4")
        self.stop = False

    def checkFolder(self):
        threading.Timer(10.0, self.checkFolder).start()
        newset = glob.glob(self.directory_to_watch + "/*.mp4")
        #diff =  set(newset) - set(self.savedSet)
        if len(newset) != 0:
            video = list(newset)[0]
            print("Received created event - ", video)
            self.processFile(video)
        for file in newset:
            os.remove(file)
    
    def processFile(self, file):
        faces = self.videoAnalysis.analyze(file)
        for face in faces:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            for chatId in list(self.authChatIds.keys()):
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