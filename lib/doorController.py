"""
This class handle door controller life cycle.
"""
import requests
import json

class DoorController:
	
	def __init__(self, name):
		self.VERSION = "0.0.1"	
		self.name = str(name)
		self.masterUrl = ''
		self.masterSecret = ''
		self.configurationLoaded = 0
		self.zoneEnabled = 0
		print self.name  + " started."	
	
	def __str__(self):
		""" Prints out user-friendly string description """
		return "DoorController : " + str(self.name)	+ " running version " + self.VERSION		 
		
	def getConfiguration(self):
		""" Asks master for configuration """
		if len(self.masterUrl) > 0:
			r = requests.get(self.masterUrl + '/configuration/' + self.name)
			print r.text
			print str(r.status_code)
			if r.status_code == 200:
				#Request success
				config = json.loads(r.text)
				self.zoneId = config['zone']
				self.zoneEnabled = config['enabled']
				self.zoneDayTimeOnly = config['dayTimeOnly']
				self.masterSecret = config['secret']
				self.configurationLoaded = 1
				print "Configuration loaded."
			else:
				print "Configuration loading failed."
				self.zoneId= 1
				self.zoneEnabled = 1
				self.zoneDayTimeOnly = 0
		else:
			self.zoneId = 1
			self.zoneEnabled = 1
			self.zoneDayTimeOnly = 0
		
	def setMaster(self, masterUrl):
		""" Sets default master """
		if(not masterUrl.startswith("http")):
			print "Error, master is not an url"
			
		if masterUrl.endswith('/'):
			masterUrl = masterUrl[:-1] #Remove last '/'
			
		r = requests.get(masterUrl + '/isAlive')
		if r.status_code == 200:
			print "Setting master url to " + masterUrl
			self.masterUrl = masterUrl
			self.getConfiguration()
		else:
			print "Error, invalid master response"
		
	def validateCredential(self, cardId, secret):
		""" Validates provided credentials against master's db """
		if not self.configurationLoaded:
			print "No configuration loaded"
			return -1
			
		if len(self.masterUrl) > 0:
			print "Getting " + self.masterUrl + '/accessRule/' + str(self.zoneId) + '/' + str(cardId)
			r = requests.get(self.masterUrl + '/accessRule/' + str(self.zoneId) + '/' + str(cardId))
			if r.status_code == 200:
				return 1
			else:
				return -1
		else:
			print "Master URL not set. (" + self.masterUrl + ")"
			return -1
