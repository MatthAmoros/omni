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
