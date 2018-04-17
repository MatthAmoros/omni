#!/usr/bin/env python
"""
This is the client, this module must be run on a Raspberry PI
"""
# Raspberry PI specifics imports
import RPi.GPIO as GPIO
import lib.SimpleMFRC522 as SimpleMFRC522 #Credit to 
# Module imports
from lib.doorController import DoorController
# Flask imports
from flask import Flask
from flask import request
# Others
import sys
from uuid import getnode as get_mac
from multiprocessing import Process
from time import sleep

mockReader = 0
mustStop = 0;
nodeId = get_mac()
doorCtrl = DoorController(nodeId)
app = Flask(__name__)

# ==== Flask definitions ====
@app.route("/")
def index():
	""" Used to check if client is online """
	return str(doorCtrl),"200"
    
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
	doorCtrl.getConfiguration()

@app.route('/adopt', methods=['POST'])
def adopt():
	""" Called by new master to adopt client 
	Returns : 
				202 : Adoption OK, 
				204 : No master url provided, 
				405 : HTTP Method not allowed (must use POST), 
				403 : Master alreay registered
	"""
	if len(doorCtrl.masterUrl) == 0:
		if request.method == 'POST':
			newMaster = request.form.get('master')
			print 'Received ' + newMaster
			if newMaster!= '':
				doorCtrl.setMaster(newMaster)
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
		return doorCtrl.masterUrl

# ===========================
# 		Threads declarations
# ===========================

def startWebServer():
	""" Starts Flask """
	print "Start web server..."
	global app
	app.run(host='0.0.0.0')
	print "Web server stopped"

def startReadingLoop():
	""" Starts RFID reading loop """
	try:		
		reader = SimpleMFRC522.SimpleMFRC522()
		print "Starting reader..."
		while mustStop == 0 :
			if mockReader == 0:
				id, text = reader.read()
			else:
				sleep(5)
				id = 22554655721354687
				text = "hashedIdAndMasterSecret"
				
			result = doorCtrl.validateCredential(id, text)
			
			if result == 1:
				print "Valid !"
			else:
				print "Error"
				
			print(id)
			print(text)
	except KeyboardInterrupt:
		pass		
	finally:
		print "Reader stopped"
		GPIO.cleanup()

# ===========================
# 		Starting up
# ===========================
if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == "mock":
		mockReader = 1
		print "Started with mocked reader."
	
	#Delcare processes
	webServerThread = Process(target=startWebServer)
	rfidReaderThread = Process(target=startReadingLoop)
	#Start processes
	rfidReaderThread.start();
	webServerThread.start();

	try:
		while mustStop == 0 :
			sleep(0.3)
	except KeyboardInterrupt:
		pass

	# ===========================
	# 		Shutting down
	# ===========================
	print "Shutting down"

	#Notify threads
	mustStop = 1
	print "Notify threads to stop..."
	sleep(1)
	#Send terminate exception
	webServerThread.terminate()
	rfidReaderThread.terminate()
	#Join threads
	webServerThread.join()
	rfidReaderThread.join()

	#Cleanup GPIO handles
	GPIO.cleanup()

	print "Gracefully closed"
	sleep(1)
