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

    def start_service_async(self):
        job_thread = threading.Thread(target=self.schedule_tasks)
        job_thread.start()
        logger.info("Ping service started")

    def schedule_tasks(self):
        for camera_name, camera_value in self.config["cameras"].items():
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
        if response != 0:
            self.bot_utils.send_msg_to_logged_auth_users(camera_name, "{} is down".format(camera_name))
