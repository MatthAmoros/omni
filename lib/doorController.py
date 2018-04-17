"""
This class handle door controller life cycle.
"""
import requests

class DoorController:
	VERSION = "0.0.1"	
	NOT_BINDED = "<FREE>"
	
	def __init__(self, name):
		self.name = name
		self.masterUrl = NOT_BINDED
		print str(name)  + " started."	
	
	def __str__(self):
		""" Prints out user-friendly string description """
		description = "DoorController : " + str(self.name)
		+ " with master " + self.masterUrl 
		+ " running version " + VERSION
		+ " <br/>Configuration " + str(jsonify(self))
		return description
		
	def getConfiguration(self):
		""" Asks master for configuration """
		if self.masterUrl != NOT_BINDED:
			r = requests.get(self.masterUrl + '/configuration/' + self.name)
			if r.status_code == "200":
				#Request success
				config = json.loads(r.text)
				self.zone.id = config['zone']['id']
				self.zone.enabled = config['zone']['enabled']
				self.zone.dayTimeOnly = config['zone']['dayTimeOnly']
				print "Configuration loaded."
			else:
				print "Configuration loading failed."
				self.zone.id = 1
				self.zone.enabled = 1
				self.zone.dayTimeOnly = 0
		else:
			self.zone.id = 1
			self.zone.enabled = 1
			self.zone.dayTimeOnly = 0
		
	def setMaster(self, masterUrl):
		""" Sets default master """
		if(!masterUrl.startswith("http"))
			print "Error, master is not an url"
		if masterUrl.endswith('/'):
			masterUrl = masterUrl[:-1] #Remove last '/'
		r = requests.get(masterUrl + '/isAlive')
		if r.status_code == 200:
			self.masterUrl = masterUrl
		else:
			print "Error, invalid master response"
		
	def validateCredential(self, cardId, secret):
		""" Validates provided credentials against master's db """
		r = requests.get(self.masterUrl + '/accessRule/' + self.zone.id + '/' + cardId , headers=getCredentialsHeaders(httpVerb='GET', httpUri=requestUri, clientSecret=self.secret))
		if r.status_code == "200":
			return 1
		else:
			return -1
