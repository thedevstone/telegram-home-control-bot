import logging
import os
import importlib
from typing import Dict

from cameras.camera import Camera

logger = logging.getLogger(os.path.basename(__file__))


class CameraLoader(object):
    def __init__(self, config):
        self.config = config
        self.cameras: Dict[str, Camera] = dict()

    def load_camera_instances(self) -> Dict[str, Camera]:
        for camera_name, camera_value in self.config["cameras"].items():
            ip = self.config["cameras"][camera_name]["ip"]
            port = self.config["cameras"][camera_name]["port"]
            username = self.config["cameras"][camera_name]["username"]
            password = self.config["cameras"][camera_name]["password"]
            camera_type = self.config["cameras"][camera_name]["type"]
            module_class: str = self.config["camera-types"][camera_type]["camera-class"]
            module = "cameras.implementations.{}".format(module_class.split(".")[0])
            camera_type = self.my_import(module, module_class.split(".")[1])
            camera_instance = camera_type(ip, port, username, password)
            self.cameras[camera_name] = camera_instance
        return self.cameras

    @staticmethod
    def my_import(module, class_name) -> type:
        module = importlib.import_module(module)
        my_class = getattr(module, class_name)
        return my_class
