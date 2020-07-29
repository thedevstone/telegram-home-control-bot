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
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
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
        out_frames = []
        vcap = cv2.VideoCapture(rtsp)
        while(1):
            if (frame_index % frame_step == 0):
                if (found_faces >= face_number or frame_index >= total_frames):
                    return out_frames
                #print(frame_index) #Loading?
                ret, frame = vcap.read()
                if ret:
                    frame = cv2.resize(frame, (750, 480))
                    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

                    bodies, weights = self.hog.detectMultiScale(gray, winStride=(8,8) )
                    for (x,y,w,h) in bodies:
                        frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) 
                        crop_body = frame[y : y + h, x : x + w]
                        faces = self.face_cascade.detectMultiScale(crop_body, 1.3, 5)
                        for (fx,fy,fw,fh) in faces:
                            frame = cv2.rectangle(frame,(x+fx,y+fy),(x+fx+fw,y+fy+fh),(255,0,0),2) 
                            out_frames.append(frame)
                            #cv2.imshow('Crop face', crop_face)
                            #cv2.waitKey(0)
                            found_faces += 1
            frame_index += 1
        return out_frames

if __name__ == "__main__":
    import botUtils
    config = botUtils.loadYaml("config.yaml")
    video = VideoAnalysis(config)
    video.analyze("video.mp4")