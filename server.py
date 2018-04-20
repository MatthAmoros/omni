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
from flask import Flask, request, send_from_directory

from lib.sourceFactory import SourceFactory

CONNECTION_FILE_PATH = "./cfg/connectionString.sql" #Default
SERVER_SECRET = "DaSecretVectorUsedToHashCardId" #Default

devicesConnected = []
app = Flask(__name__, static_url_path='')

#Flask definitions
""" Front end """
#Javascript directory
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('./templates/static/js', path)

#CSS directory
@app.route('/styles/<path:path>')
def send_css(path):
    return send_from_directory('./templates/static/styles', path)

#View state
@app.route("/state")
def viewState():
	return render_template('./server/controllersView.html', devices=devicesConnected)

#View settings
@app.route("/settings")
def viewCredentials():
	return render_template('./server/settings.html')

#Main view
@app.route("/main")
def viewMain():
	return "main"

#View index
@app.route("/")
def index():
	return render_template('./server/index.html')

""" Communications endpoints """
@app.route("/isAlive")
def isAlive():
    return "200"
    
@app.route("/confirmAdopt/<clientId>")
def confirmAdopt(clientId):
	return "200"
    
@app.route("/accessRule/<zone>/<credential>", methods=['GET'])
def validateCredential(zone, credential):
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	canAccess = source.getOrCreateClientAccessRight(credential, zone)
	if canAccess == True:
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
	conf = source.loadDeviceConfiguration(clientId)
	devicesConnected.append(conf)
	return conf

def loadServerConfiguration():
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	conf = source.loadServerConfiguration()

def preStartDiagnose():
	print "Pre-start diagnostic ..."
	print "1) Loading application configuration ..."
	""" Reading configuration """
	appConfig = ConfigParser.ConfigParser()
	appConfig.read("./cfg/config.ini")
	
	print "Sections found : " + str(appConfig.sections())
	
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

#Only if it's run
if __name__ == "__main__":
	preStartDiagnose()		
		
	print "Start web server..."
	app.run(host='0.0.0.0')
