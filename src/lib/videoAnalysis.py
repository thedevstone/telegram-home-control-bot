import numpy as np
import cv2
import os
import lib.botUtils #Remove to test this class
import logging
from matplotlib import pyplot as plt

logger = logging.getLogger(os.path.basename(__file__))

class VideoAnalysis:
    def __init__(self, config):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.config = config
        self.cam_to_rstp = dict()
        self.init_rtsp()

    def init_rtsp(self):
        for key, value in self.config["network"]["cameras"].items():
            self.cam_to_rstp[str(key)] = value["rtsp"]

    def analyzeRTSP(self, camera_id: str):
        rtsp = self.cam_to_rstp[camera_id]
        analysis = self.config["analysis"]
        fps = analysis["fps"]
        seconds = analysis["seconds"]
        face_number = analysis["faces"]
        analysis_percent = analysis["sampling_percentage"]
        total_frames = fps * seconds
        frames_to_analyze = total_frames * analysis_percent
        frame_step = int(total_frames / frames_to_analyze)
        found_faces = 0
        frame_index = 0
        cropped_faces = []
        vcap = cv2.VideoCapture(rtsp)
        while(1):
            if (frame_index % frame_step == 0):
                if (found_faces >= face_number or frame_index >= total_frames):
                    return cropped_faces
                #print(frame_index) #Loading?
                ret, frame = vcap.read()
                if ret:
                    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    for (x,y,w,h) in faces:
                        frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) 
                        crop_face = frame[y : y + h, x : x + w]
                        #cropped_faces.append(crop_face)            #NO FACES ALL PHOTO
                        cropped_faces.append(frame)
                        #cv2.imshow('Crop face', crop_face)
                        #cv2.waitKey(0)
                        found_faces += 1
            frame_index += 1
        return cropped_faces

if __name__ == "__main__":
    import botUtils
    config = botUtils.loadYaml("config.yaml")
    video = VideoAnalysis(config)
    video.analyze("video.mp4")