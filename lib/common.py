"""
This class is shared between clients and servers to exchange
configuration information
"""
class ClientConfiguration:
	zone = 0
	enabled = 0
	dayTimeOnly = 0
	authorizeOnly = "" #If empty, authorize all, else groups with ';' separators
	clientId = 0
	secret = 18091992118292
	
	def __init__(self, clientId):
		self.clientId = clientId
	
	def __str___(self):
		return "Configuration : Zone : " + str(self.zone) + " Enabled : " + str(self.enabled) + " DayTimeOnly : " + str(self.dayTimeOnly) + " AuthorizeOnly : " + str(self.authorizeOnly)
		
	def serialize(self):
		return { 'zone' : self.zone, 'enabled' : self.enabled, 'dayTimeOnly' : self.dayTimeOnly, 'authorizeOnly' : self.authorizeOnly, 'secret' : self.secret }
