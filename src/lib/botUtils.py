import logging
from logging.handlers import RotatingFileHandler
import yaml
import os
from pathlib import Path

logger = logging.getLogger(os.path.basename(__file__))

def startWebHook(updater, token, ip, port, key, cert):
    r"""Start webhook.
            Parameters
            ----------
            updater : updater
                Telegram updater
            token : token
                Bot token
            ip : ip
                Public IP
            port : port
                Bot port 88
            key : key
                Cert key.
            cert : certificate
                Certificate.
    """
    ########### START WEBHOOK ##############
    updater.start_webhook(listen='0.0.0.0',
                        port = port,
                        url_path = token,
                        key = key,
                        cert = cert,
                        webhook_url='https://{}:{}/{}'.format(ip, port, token))

def initLogger():
    logname = getProjectRelativePath("app.log")
    handler = RotatingFileHandler(logname, mode="w", maxBytes=100000, backupCount=1)
    handler.suffix = "%Y%m%d"
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, handlers=[handler])
    if os.path.isfile(logname):  # log already exists, roll over!
        handler.doRollover()

def loadYaml(file):
    try: return yaml.safe_load(open(file))
    except yaml.YAMLError as e: print(e), os._exit(1)
    
def dumpYaml(data, file):
    yaml.dump(data, open(file, 'w'), default_flow_style=False)

def getProjectRelativePath(path):
    return Path.joinpath(Path(os.getcwd()).parent, path)

def checkConfiguration(config):
    def checkFileExists(path):
        return os.path.isfile(getProjectRelativePath(path))
    watch_dir = config["watchDirectory"]
    network = config["network"]
    network_path = network["key"]
    cert_path = network["cert"]
    return checkFileExists(network_path) and checkFileExists(cert_path) and watch_dir