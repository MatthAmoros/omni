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
from flask import render_template

from lib.sourceFactory import SourceFactory

CONNECTION_FILE_PATH = "./cfg/connectionString.sql" #Default
SERVER_SECRET = "DaSecretVectorUsedToHashCardId" #Default

clientCount = 0
app = Flask(__name__)

#Flask definitions
@app.route("/")
def index():
	""" Front-end """
	return render_template('./server/index.html', clientCount=str(clientCount))
	
@app.route("/isAlive")
def isAlive():
    return "200"
    
@app.route("/confirmAdopt")
def confirmAdopt():		
	global clientCount
	clientCount += 1
	return "200"
    
@app.route("/accessRule/<zone>/<credential>", methods=['GET'])
def validateCredential(zone, credential):
	if zone == '1':
		return "200"
	else:
		return "401"
    
@app.route("/configuration/<clientId>")
def configuration(clientId):
	configuration = getConfigurationByClientId(clientId)
	configuration.secret = SERVER_SECRET
	if configuration is None:
		return "401"
	print "Sending configuration for client " + str(clientId)
	return jsonify(configuration.serialize()), "200"

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
	print "Pre-start diagnostic ..."
	print "1) Loading application configuration ..."
	appConfig = ConfigParser.ConfigParser()
	appConfig.read("./cfg/config.ini")
	
	if len(appConfig.sections()) == 0:
		raise RuntimeError("Could not open configuration file")
			
	CONNECTION_FILE_PATH = appConfig.get("AppConstants", "ConnectionStringFilePath")
	SERVER_SECRET = appConfig.get("AppConstants", "Secret")
	
	print " >> Configuration OK"
	
	print "2) Trying to reach datasource..."	
	sourceDbConnection = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	dataSourceOk = sourceDbConnection.checkIsReachable()
	if dataSourceOk == 1:
		print " >> Datasource OK"
	else:
		print " >> Datasource unreachable."
		
		
	print "Start web server..."
	app.run(host='0.0.0.0')
