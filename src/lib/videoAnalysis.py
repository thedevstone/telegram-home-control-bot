import logging
import os
from io import BytesIO

import cv2
from PIL import Image

logger = logging.getLogger(os.path.basename(__file__))


class VideoAnalysis:
    def __init__(self, config, auth_chat_ids, bot):
        self.config = config
        self.authChatIds = auth_chat_ids
        self.bot = bot
        self.cam_to_rstp = dict()
        self.init_rtsp()

    def init_rtsp(self):
        for key, value in self.config["network"]["cameras"].items():
            self.cam_to_rstp[str(key)] = value["rtsp"]

    @staticmethod
    def zoom_image(frame, zoom):
        # get the webcam size
        height, width, channels = frame.shape
        # prepare the crop
        center_x, center_y = int(height / 2), int(width / 2)
        radius_x, radius_y = int(center_x * zoom), int(center_y * zoom)

        min_x, max_x = center_x - radius_x, center_x + radius_x
        min_y, max_y = center_y - radius_y, center_y + radius_y

        cropped = frame[min_x:max_x, min_y:max_y]
        # resized_cropped = cv2.resize(cropped, (width, height), cv2.INTER_CUBIC)
        return cropped

    def analyze_rtsp(self, camera_id: str):
        rtsp = self.cam_to_rstp[camera_id]
        # Warn user
        logged_users = dict((k, v) for k, v in self.authChatIds.items() if v["logged"] is True)
        for chatId, value in logged_users.items():
            self.bot.send_message(chatId, text="😳Motion detected❗\n{}".format(rtsp))
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
                    self.send_image(frame, out_image_index)
                    out_image_index += 1
                frame_index += 1
            else:
                break
        v_capture.release()

    def send_image(self, image, index):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        logged_users = dict((k, v) for k, v in self.authChatIds.items() if v["logged"] is True)
        for chatId, value in logged_users.items():
            temp_file = BytesIO()
            temp_file.name = 'MotionDetection{}.png'.format(index)
            im = Image.fromarray(image)
            im.save(temp_file, format="png")
            temp_file.seek(0)
            self.bot.send_photo(chatId, temp_file)
