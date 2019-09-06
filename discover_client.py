#!/usr/bin/env python3
"""
This script launch the discovery thread to listen for new client
"""
__version__ = '0.1'

from configparser import ConfigParser
import json
import time
from threading import Thread

from lib.datasource import DataSource
from lib.visibilityManager import VisibilityManager
from lib.common import ServerSetting, DeviceConfiguration, Member

if __name__ == "__main__":
    CONNECTION_FILE_PATH = "./cfg/connectionString.sql" #Default
else:
    CONNECTION_FILE_PATH = "/app/omni/cfg/connectionString.sql" #Default

SERVER_SECRET = "DaSecretVectorUsedToHashCardId" #Default


#Only if it's run
if __name__ == "__main__":
    """ Start discovery manager """
    visibility_manager = VisibilityManager()
    discovery_thread = Thread(target=visibility_manager.listen_for_discovery_datagram)

    discovery_thread.start()
    while True:
        time.sleep(1)
    visibility_manager.must_stop = True
    discovery_thread.join()
