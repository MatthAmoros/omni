"""
This class is shared between clients and servers to exchange
configuration information
"""
class DeviceConfiguration:
	zone = 0 #Zone Id that identify door controller location
	enabled = 0 #Controller enabled ?
	dayTimeOnly = 0 #Only enabled on day time ?
	authorizeOnly = "" #If empty, authorize all, else groups with ';' separators
	clientId = 0 #Client ID
	secret = "" #Server secret, for future cryptographic uses
	deviceType = 0
	description = ""
	
	def __init__(self, clientId):
		self.clientId = clientId
	
	def __str___(self):
		return "Configuration : " + str(description) + " Zone : " + str(self.zone) + " Enabled : " + str(self.enabled) + " DayTimeOnly : " + str(self.dayTimeOnly) + " AuthorizeOnly : " + str(self.authorizeOnly + " DeviceType : " + str(self.deviceTpe))
		
	def serialize(self):
		"""Serializes current object instance (used with jsonify)"""
		return { 'description': self.description, 'zone' : self.zone, 'enabled' : self.enabled, 'dayTimeOnly' : self.dayTimeOnly, 'authorizeOnly' : self.authorizeOnly, 'secret' : self.secret, 'deviceType' : self.deviceType}

class Member:
	token = ''
	name = ''
	lastname = ''
	
	def __init__(self, id):
		self.id = id
		self.token = ''
		self.name = ''
		self.lastname = ''
		
	def __str___(self):
		return "Member : " + str(self.id) + " | " + str(self.token) + " | " + str(self.name) + " | " + str(self.lastname) 

class ServerSetting:
	def __init__(self, settingType):
		self.type = settingType
		self.parameters = []
	
	def __str___(self):
		return "Setting : " + str(self.type) + " | " + str(self.parameters)
		
	def serialize(self):
		"""Serializes current object instance (used with jsonify)"""
		return { 'type': self.type, 'parameters' : self.parameters}
