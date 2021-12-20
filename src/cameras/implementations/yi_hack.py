import requests

from cameras.camera import Camera


class YiHack(Camera):
    def get_snapshot(self):
        snapshot_url = "/cgi-bin/snapshot.sh"
        response = requests.get(
            "http://{}:{}{}&username={}&password={}"
            .format(self.ip, self.port, snapshot_url, self.username, self.password), timeout=10)
        return response

    def get_video(self, video_oldness: int):
        video_url = "/cgi-bin/getlastrecordedvideo.sh"
        response = requests.get(
            "http://{}:{}{}&username={}&password={}"
            .format(self.ip, self.port, video_url, self.username, self.password), timeout=10)
        return response
