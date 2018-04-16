import requests

class DoorController:	
	def __init__(self, name):
		self.name = name
		self.masterUrl = ''
		print name  + " started."
		
	def getConfiguration(self):
		#Query server for configuration
		self.zone.id = 1
		self.zone.enabled = 1
		self.zone.dayTimeOnly = 0
		
	def setMaster(self, masterUrl):
		if masterUrl.endswith('/'):
			masterUrl = masterUrl[:-1] #Remove last '/'
		r = requests.get(masterUrl + '/isAlive')
		if r.status_code == 200:
			self.masterUrl = masterUrl
		else:
			print "Error, invalid master response"
		
	def validateCredential(self, cardId, secret):
		#Validate cardId secret combination
		#Query for zone
		r = requests.get(self.masterUrl + '/accessRule/' + self.zone.id + '/' + cardId , headers=getCredentialsHeaders(httpVerb='GET', httpUri=requestUri, clientSecret=self.secret))
		if r.status_code == "200":
			return 1
		else:
			return -1
