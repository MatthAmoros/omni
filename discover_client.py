#!/usr/bin/env python3
"""
This script launch the discovery thread to listen for new client
"""
__version__ = '0.1'

from configparser import ConfigParser
import json
import time
from threading import Thread

from lib.sourceFactory import SourceFactory
from lib.visibilityManager import VisibilityManager
from lib.common import ServerSetting, DeviceConfiguration, Member

if __name__ == "__main__":
    CONNECTION_FILE_PATH = "./cfg/connectionString.sql" #Default
else:
    CONNECTION_FILE_PATH = "/app/omni/cfg/connectionString.sql" #Default

SERVER_SECRET = "DaSecretVectorUsedToHashCardId" #Default


def pre_start_diagnose():
	print("Pre-start diagnostic ...")
	print("1) Loading application configuration ...")

	""" Reading configuration """
	appConfig = ConfigParser()
	appConfig.read('./cfg/config.ini')

	print("Sections found : " + str(appConfig.sections()))

	if len(appConfig.sections()) == 0:
		raise RuntimeError("Could not open configuration file")

	CONNECTION_FILE_PATH = appConfig.get("AppConstants", "ConnectionStringFilePath")
	SERVER_SECRET = appConfig.get("AppConstants", "Secret")

	print(" >> Configuration OK")

	print("2) Trying to reach datasource...")
	sourceDbConnection = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	dataSourceOk = sourceDbConnection.is_reachable()
	if dataSourceOk == 1:
		print(" >> Datasource OK")
	else:
		print(" >> Datasource unreachable.")


#Only if it's run
if __name__ == "__main__":
    pre_start_diagnose()

    """ Start discovery manager """
    visibility_manager = VisibilityManager()
    discovery_thread = Thread(target=visibility_manager.listen_for_discovery_datagram)

    discovery_thread.start()
    while True:
        time.sleep(1)
    visibility_manager.must_stop = True
    discovery_thread.join()
