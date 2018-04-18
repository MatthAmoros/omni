#!/usr/bin/env python
"""
This script launch the server, used as a master to handle 
clients configuration and validate credentials.

It can be run on any platform with python and flask installed
"""
import ConfigParser

from flask import Flask
from flask import request
from flask import jsonify

from lib.sourceFactory import SourceFactory
CONNECTION_FILE_PATH = "../cfg/connectionString.sql" #Default
app = Flask(__name__)

#Flask definitions
@app.route("/isAlive")
def index():
    return "200"
    
@app.route("/accessRule/<zone>/<credential>", methods=['GET'])
def validateCredential(zone, credential):
	if zone == '1':
		return "200"
	else:
		return "401"
    
@app.route("/configuration/<clientId>")
def configuration(clientId):
	print clientId + " requested configuration."
	configuration = getConfigurationByClientId(clientId)
	return jsonify(configuration.serialize())

def getConfigurationByClientId(clientId):
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	conf = source.loadClientConfiguration(clientId)
	return conf

def loadServerConfiguration():
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	conf = source.loadServerConfiguration()


#Only if it's run
if __name__ == "__main__":
	""" Reading configuration """
	"""
	appConfig = ConfigParser.ConfigParser()
	appConfig.read("../cfg/config.ini")
	CONNECTION_FILE_PATH = appConfig.get("AppConstants", "ConnectionStringFilePath") """
	
	print "Start web server..."
	app.run(host='0.0.0.0')
