#!/usr/bin/env python3
"""
This is the client, it starts a web server to handle basic communication
with the master then runs a device_loop that while act depending on loaded configuration
"""
__version__ = '0.2'

import sys
import requests
import json
import threading

# Module imports
try:
	from lib.devices.deviceFactory import DeviceFactory
	from lib.devices.deviceBase import DeviceBase
	from lib.visibilityManager import VisibilityManager
	from lib.common import DeviceStatus, PrintColor
except ModuleNotFoundError:
	sys.exit("Business modules not found")
else:
	from flask import Flask
	from flask import request
	from flask import jsonify
	from uuid import getnode as get_mac
	from threading import Thread
	from time import sleep

adopted = False

application_stopping = False
node_id = get_mac()
device_object = DeviceBase(node_id)
device_factory = DeviceFactory(node_id)
app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
	""" Used to check if client is online """
	return str("Device is running."), 200

# ==== Flask definitions ====
@app.route("/GPIO", methods=['GET'])
def get_gpio():
	global deviceObject
	""" Used to get device GPIO state"""
	return str(device_object.get_status()), 200

@app.route("/shutdown")
def shutdown():
	global deviceObject
	if device_object.is_running == False:
		shutdownFunc = request.environ.get('werkzeug.server.shutdown')
		if shutdownFunc is None:
			raise RuntimeError('Not running with the Werkzeug Server')
		shutdownFunc()
	else:
		print("Must stop with local device running ?")
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/isNodeFree")
def is_node_free():
	""" Called to check if a master has been associated """
	if len(device_object.master_url) == 0:
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
	else:
		return json.dumps({'success':False}), 409, {'ContentType':'application/json'}

@app.route('/reloadConfiguration', methods=['POST'])
def load_configuration():
	""" Called by master to force reload configuration """
	global device_object
	device_object = device_factory.get_configuration()

	return json.dumps({'success':device_object.is_in_error}), 200, {'ContentType':'application/json'}

@app.route('/adopt', methods=['POST'])
def adopt():
	""" Called by new master to adopt client
	Returns :
				202 : Adoption OK,
				204 : No master url provided,
				405 : HTTP Method not allowed (must use POST),
				403 : Master alreay registered
	"""
	if len(device_factory.master_url) == 0:
		global adopted
		new_master_url = request.form.get('master')

		if new_master_url != '':
			""" Try with provided url """
			device_factory.set_master(new_master_url)
		else:
			""" Without master url provided, try with caller url and default port """
			remote_url = 'http://' + str(request.remote_addr) + ':5000'
			device_factory.set_master(remote_url)

		""" Success """
		load_configuration()
		adopted = True
		return json.dumps({'success':True}), 202, {'ContentType':'application/json'}
	else:
		return json.dumps({'success':False}), 403, {'ContentType':'application/json'}

@app.route('/adopt', methods=['GET'])
def get_master():
	""" Returns current master """
	if request.method == 'GET':
		return device_factory.master_url

@app.route('/state', methods=['GET'])
def get_status():
	""" Returns current configuraiton """
	device_status = DeviceStatus(device_object.name, device_object.is_in_error, device_object.error_status)
	return jsonify(device_status.serialize()), 200, {'ContentType':'application/json'}

# ===========================
# 	Threads declarations
# ===========================
def start_web_server():
	""" Starts Flask """
	print("Start web server...")
	global app
	app.run(host='0.0.0.0', port=int("5555"))
	print(PrintColor.OKGREEN + "Web server stopped")

def start_device_loop():
	""" Starts device loop """
	try:
		global adopted
		global device_object
		print(PrintColor.OKGREEN + "Starting device ...")
		visibility_manager = VisibilityManager()

		while application_stopping == False:
			if device_object.is_zone_enabled == True and device_object.is_running == False:
				print(PrintColor.OKGREEN + "Initialize main device loop on thread " + str(threading.get_ident()) + ", device type " + str(device_object.type))
				if device_object.type != "NONE":
					device_object.run()

			if adopted == False:
				""" Run discovery mode """
				print(PrintColor.OKBLUE + "Broadcasting discovery message")
				visibility_manager.send_discovery_datagram()
				sleep(15)
	finally:
		print("Gracefully closed device loop")

def main():
	""" Main method, handle startup and shutdown """

	#Delcare processes
	web_server_thread = Thread(target=start_web_server)
	device_thread = Thread(target=start_device_loop)
	#Start processes
	device_thread.start()
	web_server_thread.start()

	try:
		while True:
			sleep(0.3)
	except KeyboardInterrupt:
		pass

	# ===========================
	# 		Shutting down
	# ===========================
	print(PrintColor.WARNING + "Shutting down")

	#Notify threads
	print(PrintColor.WARNING + "Notify threads to stop...")

	""" First, stop device thread """
	global device_object
	global application_stopping

	application_stopping = True

	try:
		device_object.stop_loop()
	except NotImplementedError:
		pass

	device_thread.join()
	device_object.is_running = False

	""" Then, send kill command to endpoint """
	requests.get("http://localhost:5555/shutdown")

	web_server_thread.join()

	#Join threads
	print(PrintColor.OKGREEN + "Done.")

# ===========================
# 		Starting up
# ===========================
if __name__ == "__main__":
	main()
