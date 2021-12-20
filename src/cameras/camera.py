from abc import ABC, abstractmethod


class Camera(ABC):
    def __init__(self, ip: str, port: int, username: str, password: str):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    @abstractmethod
    def get_snapshot(self):
        ...

    @abstractmethod
    def get_video(self, video_oldness: int):
        ...
