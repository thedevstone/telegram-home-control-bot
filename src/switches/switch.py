from abc import ABC, abstractmethod
from typing import Dict


class Switch(ABC):
    def __init__(self, name: str, ip: str, port: int, username: str, password: str, services: Dict):
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.services: Dict = services

    @abstractmethod
    def switch_on(self):
        ...

    @abstractmethod
    def switch_off(self):
        ...

    @abstractmethod
    def toggle(self):
        ...

    @abstractmethod
    def inpulse(self):
        ...
