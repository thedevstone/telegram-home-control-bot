from abc import ABC, abstractmethod
from io import BytesIO

from requests import Response


class Camera(ABC):
    def __init__(self, ip: str, port: int, username: str, password: str):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    @abstractmethod
    def get_snapshot(self) -> bytes:
        ...

    @abstractmethod
    def get_video_times(self) -> list[str]:
        ...

    @abstractmethod
    def get_video(self, video_oldness: int) -> BytesIO:
        ...

    @abstractmethod
    def speak(self, message_data: bytes) -> Response:
        ...
