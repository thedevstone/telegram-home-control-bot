from abc import ABC, abstractmethod
from io import BytesIO
from typing import Dict

from requests import Response


class Camera(ABC):
    def __init__(self, name: str, ip: str, port: int, username: str, password: str, services: Dict):
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.services: Dict = services

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
