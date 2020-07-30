import numpy as np
import cv2
import os
from lib import botUtils #Remove to test this class
import lib.botUtils
import logging
#import dlib
from matplotlib import pyplot as plt

logger = logging.getLogger(os.path.basename(__file__))

class VideoAnalysis:
    def __init__(self, config):
        self.net = self.initDNN()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.config = config
        self.cam_to_rstp = dict()
        self.init_rtsp()
        #self.face_detect = dlib.get_frontal_face_detector()

    def initDNN(self):
        DNN = "TF"
        if DNN == "CAFFE":
            modelFile = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
            configFile = "deploy.prototxt"
            return cv2.dnn.readNetFromCaffe(configFile, modelFile)
        else:
            modelFile = "models/opencv_face_detector_uint8.pb"
            configFile = "models/opencv_face_detector.pbtxt"
            return  cv2.dnn.readNetFromTensorflow(modelFile, configFile)

    def init_rtsp(self):
        for key, value in self.config["network"]["cameras"].items():
            self.cam_to_rstp[str(key)] = value["rtsp"]
    
    def getConfig(self):
        analysis = self.config["analysis"]
        fps = analysis["fps"]
        seconds = analysis["seconds"]
        face_number = analysis["faces"]
        anal_fps = analysis["anal_fps"]
        total_frames = fps * seconds
        frame_step = int(fps / anal_fps)
        return (face_number, total_frames, frame_step)

    def detectFaceHaar(self, frame):
        frameHaar = frame.copy()
        faces = self.face_cascade.detectMultiScale(frameHaar, 1.1, 5, 40)
        bboxes = []
        for (x,y,w,h) in faces:
            cvRect = [(x, y, w, h)]
            bboxes.append(cvRect)
            frameHaar = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) 
        return frameHaar, len(bboxes)


    def detectFaceDlibHog(self, frame, inHeight=300, inWidth=0):
        frameHOG = frame.copy()
        frameHeight = frameHOG.shape[0]
        frameWidth = frameHOG.shape[1]
        frameDlibHogSmall = cv2.cvtColor(frameHOG, cv2.COLOR_BGR2RGB)
        faceRects = self.face_detect(frameDlibHogSmall, 0)
        bboxes = []
        for faceRect in faceRects:
            cvRect = [int(faceRect.left()), int(faceRect.top()),
                    int(faceRect.right()), int(faceRect.bottom()) ]
            bboxes.append(cvRect)
            cv2.rectangle(frameHOG, (cvRect[0], cvRect[1]), (cvRect[2], cvRect[3]), (0, 255, 0), int(round(frameHeight/150)), 4)
        return frameHOG, len(bboxes)

    def detectFaceOpenCVDnn(self, frame):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], False, False)

        self.net.setInput(blob)
        detections = self.net.forward()
        bboxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.3:
                print(confidence)
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([x1, y1, x2, y2])
                cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
        return frameOpencvDnn, len(bboxes)

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
        face_number, total_frames, frame_step = self.getConfig()
        found_faces = 0
        frame_index = 0
        out_frames = []
        vcap = cv2.VideoCapture(rtsp)
        while(1):
            ret, frame = vcap.read()
            if (frame_index % frame_step == 0):
                if (found_faces >= face_number or frame_index >= total_frames):
                    return out_frames
                print(frame_index) #Loading?
                if ret:
                    zoomed = self.zoomImage(frame, 0.4)
                    frame_face, n_faces = self.detectFaceOpenCVDnn(zoomed)
                    if (n_faces > 0):
                        out_frames.append(frame)
                        found_faces += 1
                        '''cv2.imshow('my webcam', frame_face)
                        if cv2.waitKey(1) == 27: 
                            break  # esc to quit'''
                        
            frame_index += 1
        #cv2.destroyAllWindows()
        return out_frames

if __name__ == "__main__":
    import botUtils
    config = botUtils.loadYaml("config.yaml")
    video = VideoAnalysis(config)
    video.analyze("video.mp4")