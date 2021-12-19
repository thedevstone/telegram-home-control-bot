from typing import List

import requests


def get_last_folder_video_times(ip: str, port: int) -> List[str]:
    folders = requests.get("http://{}:{}/cgi-bin/eventsdir.sh".format(ip, port)).json()
    dirname = folders["records"][0]["dirname"]
    last_folder_videos = requests.get("http://{}/cgi-bin/eventsfile.sh?dirname={}".format(ip, dirname)).json()
    video_times = [str(video_entry["time"]).removeprefix("Time: ") for video_entry in last_folder_videos["records"]]
    return video_times


if __name__ == '__main__':
    get_last_folder_video_times("yi.cam")
