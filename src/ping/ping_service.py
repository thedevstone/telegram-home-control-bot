import logging
import os
import threading
import time

import schedule

from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(os.path.basename(__file__))


class PingService:
    def __init__(self, utils: BotUtils, config):
        self.bot_utils = utils
        self.config = config
        self.mutex = threading.Lock()
        self.health_checks = dict()

    def start_service_async(self):
        job_thread = threading.Thread(target=self.schedule_tasks)
        job_thread.start()
        logger.info("Ping service started")

    def schedule_tasks(self):
        for camera_name, camera_value in self.config["cameras"].items():
            self.health_checks[camera_name] = True  # Suppose al cameras up and working
            ip = camera_value["ip"]
            ping = camera_value["ping-time"]
            schedule.every(ping).seconds.do(self.run_threaded, self.ping_camera, camera_name, ip)
        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def run_threaded(job_func, *args, **kwargs):
        job_thread = threading.Thread(target=job_func, args=args, kwargs=kwargs)
        job_thread.start()

    def ping_camera(self, camera_name, ip):
        response = os.system("ping -c 1 {} > /dev/null 2>&1".format(ip))
        self.mutex.acquire()
        if response != 0 and self.health_checks.get(camera_name):
            self.bot_utils.send_msg_to_logged_auth_users(camera_name, "{} is down".format(camera_name))
            self.health_checks[camera_name] = False
        elif response == 0 and not self.health_checks.get(camera_name):
            self.bot_utils.send_msg_to_logged_auth_users(camera_name, "{} is up".format(camera_name))
            self.health_checks[camera_name] = True
        self.mutex.release()
