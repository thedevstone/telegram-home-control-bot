import time
import os
import matplotlib.pyplot as plt
import matplotlib
import cv2
import logging
import telegram
from PIL import Image
from io import BytesIO
from lib import videoAnalysis, botUtils
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    def __init__(self, directory_to_watch, videoAnalysis, authChatIds, bot):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch
        self.videoAnalysis = videoAnalysis
        self.authChatIds = authChatIds
        self.bot = bot

    def run(self):
        event_handler = WatchDogHandler(self.videoAnalysis, self.authChatIds, self.bot)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()

class WatchDogHandler(FileSystemEventHandler):
    def __init__(self, videoAnalysis, authChatIds, bot):
        self.videoAnalysis = videoAnalysis
        self.authChatIds = authChatIds
        self.bot = bot

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            file = botUtils.getProjectRelativePath(event.src_path)
            print("Received created event - ", file)
            if (file.name.endswith('.mp4')):
                faces = self.videoAnalysis.analyze(file.as_posix())
                for face in faces:
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                    for chatId in list(self.authChatIds.keys()):
                        temp_file = BytesIO()
                        temp_file.name = 'temp.png'
                        im = Image.fromarray(face)
                        im.save(temp_file, format="png")
                        temp_file.seek(0)
                        self.bot.send_photo(chatId, temp_file)
                    #print(face) #cannot see image from different thread
            else:
                print("Not a video file")
            #os.remove(event.src_path)

        elif event.event_type == 'deleted':
            pass
            # Taken any action here when a file is modified.
            #print("Received deleted event - ", event.src_path)

if __name__ == "__main__":
    videoAnalysis = videoAnalysis.VideoAnalysis()
    watcher = Watcher(".", videoAnalysis)
    watcher.run()