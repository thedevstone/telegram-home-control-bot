import logging
import os

import paho.mqtt.client as mqtt

logger = logging.getLogger(os.path.basename(__file__))


class MqttClient:
    def __init__(self, video_analysis, auth_chat_ids, bot, config):
        self.videoAnalysis = video_analysis
        self.authChatIds = auth_chat_ids
        self.bot = bot
        self.config = config
        self.client = mqtt.Client(client_id="Bot", clean_session=True)
        self.init_mqtt_client()

    def init_mqtt_client(self):
        username = self.config["network"]["mqtt"]["username"]
        password = self.config["network"]["mqtt"]["password"]
        self.client.username_pw_set(username=username, password=password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT Connected with result code " + str(rc))
        for key, value in self.config["network"]["cameras"].items():
            self.client.subscribe("{}".format(value["topic"]), qos=1)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        message = str(msg.payload.decode("utf-8"))
        camera_id = str(msg.topic).split('/')[0]
        status = self.config["analysis"]["status"]
        if message == "motion_start" and status:
            self.motion_start(camera_id)

    def connect_and_start(self):
        server = self.config["network"]["mqtt"]["server"]
        self.client.connect(server, 1883, 60)
        self.client.loop_start()

    def disconnect_and_stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def motion_start(self, camera_id):
        self.videoAnalysis.analyze_rtsp(camera_id)
