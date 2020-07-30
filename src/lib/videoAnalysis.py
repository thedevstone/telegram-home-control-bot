import numpy as np
import cv2
import os
from lib import botUtils #Remove to test this class
import lib.botUtils
import logging
from telegram import ParseMode
from PIL import Image
from io import BytesIO
from matplotlib import pyplot as plt

logger = logging.getLogger(os.path.basename(__file__))

class VideoAnalysis:
    def __init__(self, config, authChatIds, bot):
        self.config = config
        self.authChatIds = authChatIds
        self.bot = bot
        self.cam_to_rstp = dict()
        self.init_rtsp()

    def init_rtsp(self):
        for key, value in self.config["network"]["cameras"].items():
            self.cam_to_rstp[str(key)] = value["rtsp"]

    def zoomImage(self, frame, zoom):
        #get the webcam size
        height, width, channels = frame.shape
        #prepare the crop
        centerX,centerY=int(height/2),int(width/2)
        radiusX,radiusY = int(centerX*zoom), int(centerY*zoom)

        minX,maxX=centerX-radiusX,centerX+radiusX
        minY,maxY=centerY-radiusY,centerY+radiusY

        cropped = frame[minX:maxX, minY:maxY]
        resized_cropped = cv2.resize(cropped, (width, height), cv2.INTER_CUBIC)
        return cropped

    def analyzeRTSP(self, camera_id: str):
        rtsp = self.cam_to_rstp[camera_id]
        #Warn user
        logged_users = dict((k, v) for k, v in self.authChatIds.items() if v["logged"] == True)
        for chatId, value in logged_users.items():
            self.bot.send_message(chatId,text="😳Motion detected❗\n{}".format(rtsp))
        #Init
        analysis = self.config["analysis"]
        fps = analysis["fps"]
        seconds = analysis["seconds"]
        face_number = analysis["faces"]
        total_frames = fps * seconds
        frame_separation = int(total_frames / face_number) 
        frame_index = 0
        out_image_index = 0
        vcap = cv2.VideoCapture(rtsp)
        while(1):
            ret, frame = vcap.read()
            if (frame_index < total_frames):
                if (frame_index % frame_separation == 0 and ret):
                    self.sendImage(frame, out_image_index)
                    out_image_index += 1
                frame_index += 1
            else: break
        vcap.release()

    def sendImage(self, image, index):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        logged_users = dict((k, v) for k, v in self.authChatIds.items() if v["logged"] == True)
        for chatId, value in logged_users.items():
            temp_file = BytesIO()
            temp_file.name = 'MotionDetection{}.png'.format(index)
            im = Image.fromarray(image)
            im.save(temp_file, format="png")
            temp_file.seek(0)
            self.bot.send_photo(chatId, temp_file)