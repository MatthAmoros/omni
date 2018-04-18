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

	def loadConfiguration(self, clientId):
		""" Loads configuration for specified clientId and returns it as an object """
		if self.sourceType == self.TYPE_DATABASE:
			""" If we are using a Database, self.parameter must contains a path
			 to the file that contains connection string information """		

			connectionFile = configparser.ConfigParser()
			connectionFile.read(self.parameter)
			
			connectionString = "DRIVER={"+ connectionFile.get("ConnectionString", "driver") +"};"
			connectionString += "SERVER=tcp:" + connectionFile.get("ConnectionString", "server") + ';'		
			connectionString +=  "DATABASE=" + connectionFile.get("ConnectionString", "database") + ';'
			#connectionString += "Persist Security Info=True;"
			
			#connectionString = "DSN=AccesControl;"
			""" Check if we are using trusted connection """
			if connectionFile.get("ConnectionString", "trusted") != 'yes':
				connectionString += "UID=" + connectionFile.get("ConnectionString", "user") + ';'
				connectionString += "PWD=" + connectionFile.get("ConnectionString", "password")
			else:
				connectionString += "Trusted_Connection=yes;"

			print "Connection string " + connectionString			

			cnxn = pyodbc.connect(connectionString)
			
			try:
				cnxn = pyodbc.connect(connectionString)
				cursor = cnxn.cursor()
				cursor.execute('SELECT @@version;')

				for row in cursor:
					print('row = %r' % (row,))
			except:
				print "Could not connect to provided connection."			
			
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
