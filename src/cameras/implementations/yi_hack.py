import logging
import os

import requests
from requests import Response

from cameras.camera import Camera

logger = logging.getLogger(os.path.basename(__file__))
base_url = "http://{}:{}{}"


class YiHack(Camera):
    def get_snapshot(self) -> Response:
        snapshot_url = "/cgi-bin/snapshot.sh"
        response = requests.get(
            base_url.format(self.ip, self.port, snapshot_url), timeout=10)
        return response

    def get_video_times(self) -> list[str]:
        video_folders = "/cgi-bin/eventsdir.sh"
        folders = requests.get(base_url.format(self.ip, self.port, video_folders)).json()
        dirname = folders["records"][0]["dirname"]
        video_times = "/cgi-bin/eventsfile.sh"
        last_folder_videos = requests.get(
            base_url.format(self.ip, self.port, video_times) + "?dirname={}".format(dirname)).json()
        video_times = [str(video_entry["time"]).removeprefix("Time: ") for video_entry in last_folder_videos["records"]]
        return video_times

    def get_video(self, video_oldness: int) -> Response:
        video_url = "/cgi-bin/getlastrecordedvideo.sh"
        response = requests.get(
            base_url.format(self.ip, self.port, video_url) + "?oldness={}&type=4".format(video_oldness), timeout=10)
        return response

    def speak(self, message: str) -> Response:
        speak_url = "/cgi-bin/speak.sh?lang=it-IT"
        response: Response = requests.post(
            base_url.format(self.ip, speak_url, self.port, speak_url), timeout=20, data=message)
        return response

