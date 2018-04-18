"""
This class return a data source according to source type.
Then it handle basic data source interactions
"""
import configparser #ConfigParser class
import pyodbc  #For MS SQL connection, via odbc

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
		
	def buildConnectionString(self):		
		connectionFile = configparser.ConfigParser()
		connectionFile.read(self.parameter)
		
		connectionString = "DRIVER={"+ connectionFile.get("ConnectionString", "driver") +"};" 
		connectionString += "SERVER=" + connectionFile.get("ConnectionString", "server") + ';' + "PORT=49225;"		
		connectionString +=  "DATABASE=" + connectionFile.get("ConnectionString", "database") + ';'

		""" Check if we are using trusted connection """
		if connectionFile.get("ConnectionString", "trusted") != 'yes':
			connectionString += "UID=" + connectionFile.get("ConnectionString", "user") + ';'
			connectionString += "PWD=" + connectionFile.get("ConnectionString", "password")
		else:
			connectionString += "Trusted_Connection=yes;"
			
		return connectionString
	
	def loadServerConfiguration(self):
		""" If we are using a Database, self.parameter must contains a path
		 to the file that contains connection string information """		
		connectionString = self.buildConnectionString()
		"""
		print "Connection string " + connectionString
			
		try:
			cnxn = pyodbc.connect(connectionString)
			cursor = cnxn.cursor()
			print "Retrieving configuration for client " +  str(clientId)
			cursor.execute('SELECT * FROM Controller WHERE ControllerCode =' + str(clientId))

			for row in cursor:
				str(row)
				
				config.zone = row[2]
				config.enabled = row[3]
				print str(config.serialize())
		except:
			print "Could not connect to provided connection."			
			
		return config		   
		"""

	def loadClientConfiguration(self, clientId):
		""" Loads configuration for specified clientId and returns it as an object """
		config = ClientConfiguration(clientId)
		if self.sourceType == self.TYPE_DATABASE:
			""" If we are using a Database, self.parameter must contains a path
			 to the file that contains connection string information """		
			connectionString = self.buildConnectionString()

			print "Connection string " + connectionString
				
			try:
				cnxn = pyodbc.connect(connectionString)
				cursor = cnxn.cursor()
				print "Retrieving configuration for client " +  str(clientId)
				cursor.execute('SELECT * FROM Controller WHERE ControllerCode =' + str(clientId))

				for row in cursor:
					str(row)
					
					config.zone = row[2]
					config.enabled = row[3]
					print str(config.serialize())
			except:
				print "Could not connect to provided connection."					   
				
			return config
		elif self.sourceType == self.TYPE_FILE:
			#Load from provided path
			print "From file"
		elif self.sourceType == self.TYPE_WEB:
			#Load from provided url	
			print "From URL"
