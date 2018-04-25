#!/usr/bin/env python
"""
This is the client, this module must be run on a Raspberry PI
"""
# Module imports
from lib.devices.deviceFactory import DeviceFactory
from lib.devices.deviceBase import DeviceBase
from lib.visibilityManager import VisibilityManager

# Flask imports
from flask import Flask
from flask import request
# Others
import sys
import requests
from uuid import getnode as get_mac
from threading import Thread
from time import sleep

adopted = False

applicationStopping = False
nodeId = get_mac()
deviceObject = DeviceBase(nodeId)
deviceFactory = DeviceFactory(nodeId)
app = Flask(__name__)

# ==== Flask definitions ====
@app.route("/")
def index():
	""" Used to check if client is online """
	return str(doorCtrl),"200"

@app.route("/shutdown")
def shutdown():
	global deviceObject
	if deviceObject.isRunning == False:
		shutdownFunc = request.environ.get('werkzeug.server.shutdown')		
		if shutdownFunc is None:
			raise RuntimeError('Not running with the Werkzeug Server')		
		shutdownFunc()
	else:
		print "Must stop with local device running ?"
	return "200"
	
    
@app.route("/isNodeFree")
def isNodeFree():
	""" Called to check if a master has been associated """
	if len(doorCtrl.masterUrl) == 0:
		return "200" # Available for adoption
	else:
		return "409" # Conflict

@app.route('/reloadConfiguration', methods=['POST'])
def loadConfiguration():
	""" Called by master to force reload configuration """
	global deviceObject
	deviceObject = deviceFactory.getConfiguration()
	return "200";

@app.route('/adopt', methods=['POST'])
def adopt():
	""" Called by new master to adopt client 
	Returns : 
				202 : Adoption OK, 
				204 : No master url provided, 
				405 : HTTP Method not allowed (must use POST), 
				403 : Master alreay registered
	"""
	if len(deviceFactory.masterUrl) == 0:
		if request.method == 'POST':
			newMaster = request.form.get('master')
			print 'Received ' + newMaster
			if newMaster!= '':
				deviceFactory.setMaster(newMaster)
				loadConfiguration()
				global adopted
				adopted = True
				return "202" # Accepted
			else:
				return "204" # No content
		else:
			return "405" # Method not allowed
	else:
		return "403" # Forbidden
			
			
@app.route('/adopt', methods=['GET'])
def getMaster():
	""" Returns current master """
	if request.method == 'GET':
		return deviceFactory.masterUrl

# ===========================
# 		Threads declarations
# ===========================

def startWebServer():
	""" Starts Flask """
	print "Start web server..."
	global app
	app.run(host='0.0.0.0', port=int("5555"))
	print "Web server stopped"

def startDeviceLoop():
	""" Starts RFID reading loop """
	try:
		print "Starting device ..."
		visibilityManager = VisibilityManager()
		
		while applicationStopping == False:
			global deviceObject
			if deviceObject.zoneEnabled == True and deviceObject.isRunning == False:
				runWorker = False
				deviceObject.run()
				
			if adopted == False:
				""" Run discovery mode """
				visibilityManager.sendDiscoveryDatagram()
				
			sleep(5)				
	finally:
		print "Gracefully closed device loop"

def main():
	""" Main method, handle startup and shutdown """
	
	#Delcare processes
	webServerThread = Thread(target=startWebServer)
	deviceThread = Thread(target=startDeviceLoop)
	#Start processes
	webServerThread.start()
	deviceThread.start()
	
	try:
		while True:
			sleep(0.3)
	except KeyboardInterrupt:
		pass

	# ===========================
	# 		Shutting down
	# ===========================
	print "Shutting down"

	#Notify threads

	print "Notify threads to stop..."
	""" First, stop device thread """
	global deviceObject
	global applicationStopping
	applicationStopping = True
	
	try:
		deviceObject.stopLoop()
	except NotImplementedError:
		pass
		
	deviceThread.join()	
	deviceObject.isRunning = False
	
	""" Then, send kill command to endpoint """
	requests.get("http://localhost:5555/shutdown")
		
	webServerThread.join()
	
	sleep(1)
	#Join threads
	print "Done."

# ===========================
# 		Starting up
# ===========================
if __name__ == "__main__":
	main()
