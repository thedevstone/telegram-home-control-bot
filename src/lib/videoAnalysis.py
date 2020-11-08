import logging
import os
from io import BytesIO

import cv2
from PIL import Image

from lib import telegramBot

logger = logging.getLogger(os.path.basename(__file__))


class VideoAnalysis:
    def __init__(self, config, auth_chat_ids, telegram_bot):
        self.config = config
        self.authChatIds = auth_chat_ids
        self.telegram_bot: telegramBot = telegram_bot
        self.cam_to_rstp = dict()
        self.init_rtsp()

    def init_rtsp(self):
        for key, value in self.config["network"]["cameras"].items():
            self.cam_to_rstp[str(key)] = value["rtsp"]

    def analyze_rtsp(self, camera_id: str):
        rtsp = self.cam_to_rstp[camera_id]
        # Warn user
        self.telegram_bot.send_msg_to_logged_users("😳Motion detected❗\n{}".format(rtsp))
        # Init
        analysis = self.config["analysis"]
        fps = analysis["fps"]
        seconds = analysis["seconds"]
        face_number = analysis["faces"]
        total_frames = fps * seconds
        frame_separation = int(total_frames / face_number)
        frame_index = 0
        out_image_index = 0
        v_capture = cv2.VideoCapture(rtsp)
        while 1:
            ret, frame = v_capture.read()
            if frame_index < total_frames:
                if frame_index % frame_separation == 0 and ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.send_image(frame, camera_id, out_image_index)
                    out_image_index += 1
                frame_index += 1
            else:
                break
        v_capture.release()

    def send_image(self, image, camera_id, index):
        temp_file = BytesIO()
        temp_file.name = 'Detection: {}-{}.png'.format(camera_id, index)
        im = Image.fromarray(image)
        im.save(temp_file, format="png")
        temp_file.seek(0)
        self.telegram_bot.send_image_to_logged_users(temp_file)
