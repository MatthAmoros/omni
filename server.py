#!/usr/bin/env python3
"""
This script launch the server, used as a master to handle
clients configuration and validate credentials.

It can be run on any platform with python and pip requierments installed
"""
__version__ = '0.1'

from configparser import ConfigParser
import json
from threading import Thread

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import Flask, request, send_from_directory

from lib.sourceFactory import SourceFactory
from lib.visibilityManager import VisibilityManager
from lib.common import ServerSetting, DeviceConfiguration, Member

CONNECTION_FILE_PATH = "./cfg/connectionString.sql" #Default
SERVER_SECRET = "DaSecretVectorUsedToHashCardId" #Default

connected_devices = []
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
def view_state():
	return render_template('./server/controllersView.html', devices=devicesConnected)

#View settings
@app.route("/settings")
def view_credentials():
	""" Check devices and load settings """
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	settingAccess = ServerSetting('enroll')
	settingAccess.parameters = source.getNotEnrolledMembers()
	settings = []
	settings.append(settingAccess)
	return render_template('./server/settingsView.html', settings=settings)

@app.route("/enroll", methods=['POST'])
def enroll():
	member = Member(request.form['Id'])
	member.lastname = request.form['lastname']
	member.firstname = request.form['firstname']

	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	source.updateMemberInfo(member)

	return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

#Main view
@app.route("/main")
def view_main():
	return "main"

#View index
@app.route("/")
def view_index():
	return render_template('./server/index.html')

""" Communications endpoints """
@app.route("/isAlive")
def is_alive():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/confirmAdopt/<clientId>")
def confirm_adopt(clientId):
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/accessRule/<zone>/<credential>", methods=['GET'])
def validate_credential(zone, credential):
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	canAccess = source.get_or_create_client_access_rights(credential, zone)

	if canAccess:
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
	else:
		return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

@app.route("/configuration/<client_id>")
def configuration(client_id):
	configuration = get_configuration_by_client_id(client_id)
	configuration.secret = SERVER_SECRET

	if configuration is None:
		return json.dumps({'success':False}), 204, {'ContentType':'application/json'}

	print("Sending configuration for client " + str(client_id))
	return jsonify(configuration.serialize()), "200"

def get_configuration_by_client_id(client_id):
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	conf = source.load_device_configuration(client_id)

	""" Update list """
	for x in connected_devices:
		if x.client_id == client_id:
			connected_devices.remove(x)
			break

	connected_devices.append(conf)

	return conf

def load_server_configuration():
	source = SourceFactory(SourceFactory.TYPE_DATABASE, CONNECTION_FILE_PATH)
	conf = source.load_server_configuration()

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

	print("Start web server...")
	app.run(host='0.0.0.0', port=5000)

	visibility_manager.must_stop = True
	discovery_thread.join()
