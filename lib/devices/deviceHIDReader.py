from deviceBase import DeviceBase
from time import sleep
import requests
import json

#try:
import RPi.GPIO as GPIO
import SimpleMFRC522 as SimpleMFRC522

""" Setting output GPIO """
try:
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT)
	runningOnPi = 1
except RuntimeError:
	print "Starting without GPIO"
	runningOnPi = 0
	pass 

mustStop = 0
	
class HIDReader(DeviceBase):
	def __init__(self, name):
		self.VERSION = "0.0.1"	
		self.name = str(name)
		self.type = "NONE"
		self.masterUrl = ''
		self.masterSecret = ''
		self.configurationLoaded = 0
		self.zoneEnabled = 0
		self.isRunning = False
		self.retry = 0
		print "HID Reader built !"
		
	def mainLoop(self):
		""" Starts RFID reading loop """
		try:
			if runningOnPi == 1:		
				reader = SimpleMFRC522.SimpleMFRC522()
			print "Starting controller..."
			while self.mustStop == 0 :
				if self.zoneEnabled == 1:	
					self.isRunning = True
					""" Controller is enable, start reading """
					if runningOnPi == 1:
						id, text = reader.read()
					else:
						sleep(0.5)
						id = 22554655721354687
						text = "hashedIdAndMasterSecret"
						
					result = self.validateCredential(id, text)
					
					if result == 1:
						print str(id) + " valid !"
						if runningOnPi == 1:
							""" Send GPIO signal to open the door """
							GPIO.output(12, GPIO.HIGH)
							sleep(0.3)
							GPIO.output(12, GPIO.LOW)
					else:
						print str(id) + " error !"
				else:
					""" Controller is disable, wait for a valid configuration """
					break
		finally:
			print "Reading loop stopped"

		sleep(1)
				
	def stopLoop(self):
		if runningOnPi == 1:
			GPIO.cleanup()
			
		self.mustStop = 1

	def validateCredential(self, cardId, secret):
		""" Validates provided credentials against master's db """
		if not self.configurationLoaded:
			print "No configuration loaded"
			return -1
			
		if len(self.masterUrl) > 0:
			print "Getting " + self.masterUrl + '/accessRule/' + str(self.zoneId) + '/' + str(cardId)
			try:
				r = requests.get(self.masterUrl + '/accessRule/' + str(self.zoneId) + '/' + str(cardId))
				if r.status_code == 200:
					return 1
				else:
					return -1
			except ConnectionError:
				""" Server cannot be joined, might be a network issue, try again next time
					For now, return invalid card flag
				 """
				if self.retry < 10:					 
					self.retry += 1
					return -1
				else:
					""" Server cannot be joined, let's try to forget master and reset client """
					self.unloadDevice()
					
		else:
			print "Master URL not set. (" + self.masterUrl + ")"
			return -1
