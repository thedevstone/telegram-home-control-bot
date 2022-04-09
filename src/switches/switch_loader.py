import importlib
import logging
import os
from typing import Dict

from switches.switch import Switch

logger = logging.getLogger(os.path.basename(__file__))


class SwitchLoader(object):
    def __init__(self, config):
        self.config = config
        self.cameras: Dict[str, Switch] = dict()

    def load_switch_instances(self, services: Dict) -> Dict[str, Switch]:
        for switch_name, switch_value in self.config["switches"].items():
            ip = self.config["switches"][switch_name]["ip"]
            port = self.config["switches"][switch_name]["port"]
            username = self.config["switches"][switch_name]["username"]
            password = self.config["switches"][switch_name]["password"]
            switch_type = self.config["switches"][switch_name]["type"]
            module_class: str = self.config["switch-types"][switch_type]["switch-class"]
            module = "switches.implementations.{}".format(module_class.split(".")[0])
            switch_type = self.my_import(module, module_class.split(".")[1])
            camera_instance = switch_type(switch_name, ip, port, username, password, services)
            self.cameras[switch_name] = camera_instance
        return self.cameras

    @staticmethod
    def my_import(module, class_name) -> type:
        module = importlib.import_module(module)
        my_class = getattr(module, class_name)
        return my_class
