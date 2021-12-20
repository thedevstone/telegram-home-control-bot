from abc import ABC, abstractmethod

from requests import Response


class Camera(ABC):
    def __init__(self, ip: str, port: int, username: str, password: str):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    @abstractmethod
    def get_snapshot(self) -> Response:
        ...

    @abstractmethod
    def get_video(self, video_oldness: int) -> Response:
        ...

    @abstractmethod
    def speak(self, message: str) -> Response:
        ...
