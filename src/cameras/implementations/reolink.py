import logging
import os
from datetime import datetime as dt, timedelta, datetime
from io import BytesIO
from typing import Dict

import reolinkapi
import requests
from requests import Response

from cameras.camera import Camera
from cameras.unsupported_operation_error import UnsupportedOperationError

logger = logging.getLogger(os.path.basename(__file__))
base_url = "http://{}:{}{}&username={}&password={}"


class Reolink(Camera):
    def __init__(self, name: str, ip: str, port: int, username: str, password: str, services: Dict):
        super().__init__(name, ip, port, username, password, services)
        self.api: reolinkapi.Camera = reolinkapi.Camera(self.ip, self.username, self.password)

    def get_video_list(self, hours=1):
        start = (dt.now() - timedelta(hours=hours))
        end = dt.now()
        processed_motions = self.api.get_motion_files(start=start, end=end, streamtype='sub')
        return processed_motions

    def get_snapshot(self) -> bytes:
        snapshot_url = "/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C"
        response: bytes = requests.get(
            base_url.format(self.ip, self.port, snapshot_url, self.username, self.password), timeout=10).content
        return response

    def get_video_times(self) -> list[str]:
        times = []
        processed_motions = self.get_video_list()
        for motion in processed_motions:
            time: datetime = motion["start"]
            times.append("{}:{}".format(time.hour, time.minute))
        times.reverse()
        return times

    def get_video(self, video_oldness: int) -> BytesIO:
        processed_motions = self.get_video_list()
        processed_motion = processed_motions[video_oldness]
        self.api.get_file(processed_motion["filename"], output_path=os.path.join("./", f'motion_event.mp4'))
        with open("./motion_event.mp4", "rb") as fin:
            data = BytesIO(fin.read())
            os.remove("./motion_event.mp4")
            return data

    def speak(self, message: str) -> Response:
        raise UnsupportedOperationError("Speak api not supported")
