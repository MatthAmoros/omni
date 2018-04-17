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
	
	def __init__(clientId):
		self.clientId = clientId
		
