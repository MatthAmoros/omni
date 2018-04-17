"""
This class return a data source according to source type.
Then it handle basic data source interactions
"""
from common import ClientConfiguration
class SourceFactory:
	#Sources enum
	TYPE_DATABASE = "DB"
	TYPE_WEB = "WB"
	TYPE_FILE = "FL"
	
	def __init__(self, sourceType, parameter):
		""" Instanciates a new data source according to data type """
		assert (sourceType == "DB" or sourceType == "WB" or sourceType == "FL")
		self.sourceType = sourceType
		self.parameter = parameter

	def __str__(self):
		""" Prints out user-friendly string description """
		return "Source : Type : " + self.sourceType + " with parameter " + self.parameter

	def loadConfiguration(self, clientId):
		""" Loads configuration for specified clientId and returns it as an object """
		if self.sourceType == self.TYPE_DATABASE:
			#Load from provided connection string
			
			#MOCKED
			config = ClientConfiguration(clientId)
			config.zone = 6
			config.enabled = 1
			config.dayTimeOnly = 0;
			config.authorizeOnly = "COMPANY;GUEST"
			config.clientId = clientId
			
			return config
		elif self.sourceType == self.TYPE_FILE:
			#Load from provided path
			print "From file"
		elif self.sourceType == self.TYPE_WEB:
			#Load from provided url	
			print "From URL"
