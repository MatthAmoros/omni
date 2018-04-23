from deviceHIDReader import HIDReader
from deviceBase import DeviceBase
import requests
import json

class DeviceFactory:
	def __init__(self, name):
		self.VERSION = "0.0.1"	
		self.name = str(name)
		self.type = "NONE"
		self.masterUrl = ''
		self.masterSecret = ''
		self.configurationLoaded = 0
		self.zoneEnabled = 0
		self.isRunning = False
		return

	def getConfiguration(self):
		""" Asks master for configuration """
		device = DeviceBase(self.name)
		
		if len(self.masterUrl) > 0:
			r = requests.get(self.masterUrl + '/configuration/' + self.name)
			print r.text
			print str(r.status_code)
			if r.status_code == 200:
				#Request success
				config = json.loads(r.text)
				if config['deviceType'] == 1:
					""" HID Reader """
					device = HIDReader(self.name)
				elif config['deviceType'] == 0:
					""" None """
					device = DeviceBase(self.name)
				else:
					""" Disable """
					device = DeviceBase(self.name)
					
				device.zoneId = config['zone']
				device.zoneEnabled = config['enabled']
				device.zoneDayTimeOnly = config['dayTimeOnly']
				device.masterSecret = config['secret']
				device.configurationLoaded = 1
				device.masterUrl = self.masterUrl
						
				print "Configuration loaded."
				
				return device
			else:
				print "Configuration loading failed."
				self.zoneId= 1
				self.zoneEnabled = 1
				self.zoneDayTimeOnly = 0
				return device
		else:
			self.zoneId = 1
			self.zoneEnabled = 1
			self.zoneDayTimeOnly = 0
			return device
		
	def setMaster(self, masterUrl):
		""" Sets default master """
		if(not masterUrl.startswith("http")):
			print "Error, master is not an url"
			
		if masterUrl.endswith('/'):
			masterUrl = masterUrl[:-1] #Remove last '/'
			
		r = requests.get(masterUrl + '/confirmAdopt/' + str(self.name))
		if r.status_code == 200:
			print "Setting master url to " + masterUrl
			self.masterUrl = masterUrl
			self.getConfiguration()
		else:
			print "Error, invalid master response"
