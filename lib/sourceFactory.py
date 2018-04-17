"""
This class return a data source according to source type.
Then it handle basic data source interactions
"""
class SourceFactory:
	#Sources enum
	TYPE_DATABASE = "DB"
	TYPE_WEB = "WB"
	TYPE_FILE = "FL"
	
	def __init__(sourceType, parameter):
		""" Instanciates a new data source according to data type """
		assert (sourceType == TYPE_DATABASE or sourceType == TYPE_WEB or sourceType == TYPE_FILE)
		self.sourceType = sourceType
		self.parameter = parameter

	def __str__(self):
		""" Prints out user-friendly string description """
		return "Source : Type : " + self.sourceType + " with parameter " + self.parameter

	def loadConfiguration(clientId):
		""" Loads configuration for specified clientId and returns it as an object """
		if self.sourceType == TYPE_DATABASE:
			#Load from provided connection string
			print "Database"
		elif self.sourceType == TYPE_FILE:
			#Load from provided path
			print "File"
		elif self.sourceType == TYPE_WEB:
			#Load from provided url
			print "Web"
			
