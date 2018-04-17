"""
This class is shared between clients and servers to exchange
configuration information
"""
class ClientConfiguration:
	zone = 0 #Zone Id that identify door controller location
	enabled = 0 #Controller enabled ?
	dayTimeOnly = 0 #Only enabled on day time ?
	authorizeOnly = "" #If empty, authorize all, else groups with ';' separators
	clientId = 0 #Client ID
	secret = 18091992118292 #Server secret, for future cryptographic uses
	
	def __init__(self, clientId):
		self.clientId = clientId
	
	def __str___(self):
		return "Configuration : Zone : " + str(self.zone) + " Enabled : " + str(self.enabled) + " DayTimeOnly : " + str(self.dayTimeOnly) + " AuthorizeOnly : " + str(self.authorizeOnly)
		
	def serialize(self):
		"""Serializes current object instance (used with jsonify)"""
		return { 'zone' : self.zone, 'enabled' : self.enabled, 'dayTimeOnly' : self.dayTimeOnly, 'authorizeOnly' : self.authorizeOnly, 'secret' : self.secret }
