import logging
import os

import requests
from requests import Response

from cameras.camera import Camera
from cameras.unsupported_operation_error import UnsupportedOperationError

logger = logging.getLogger(os.path.basename(__file__))
base_url = "http://{}:{}{}&username={}&password={}"


class Reolink(Camera):
    def get_snapshot(self) -> Response:
        snapshot_url = "/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C"
        response = requests.get(
            base_url.format(self.ip, self.port, snapshot_url, self.username, self.password), timeout=10)
        return response

    def get_video_times(self) -> list[str]:
        raise UnsupportedOperationError("Video api not supported")

    def get_video(self, video_oldness: int) -> Response:
        raise UnsupportedOperationError("Video api not supported")

    def speak(self, message: str) -> Response:
        raise UnsupportedOperationError("Speak api not supported")
