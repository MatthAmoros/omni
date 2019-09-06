"""
This class return a data source according to source type.
Then it handle basic data source interactions
"""
__all__ = ['SourceFactory']
__version__ = '0.1'

from configparser import ConfigParser #ConfigParser class
import platform

if platform.processor() == "ARM":
	print("RaspberryPI detected, client mode loaded.")
else:
	import pyodbc  #For MS SQL connection, via odbc

from .common import Member, Group, DeviceConfiguration
class DataSource:
	#Sources enum
	TYPE_DATABASE = "DB"
	TYPE_WEB = "WB"
	TYPE_FILE = "FL"

	def __init__(self, source_type, parameter):
		""" Instanciates a new data source according to data type """
		assert (source_type == "DB" or source_type == "WB" or source_type == "FL")
		self.source_type = source_type
		self.parameter = parameter

	def __str__(self):
		""" Prints out user-friendly string description """
		return "Source : Type : " + self.source_type + " with parameter " + self.parameter

	def _build_connection_string(self):
		""" If we are using a Database, self.parameter must contains a path
			to the file that contains connection string information """
		connection_file = ConfigParser()
		connection_file.read(self.parameter)

		connection_string = "DRIVER={"+ connection_file.get("ConnectionString", "driver") +"};"
		connection_string += "SERVER=" + connection_file.get("ConnectionString", "server") + ';' + "PORT=49225;"
		connection_string +=  "DATABASE=" + connection_file.get("ConnectionString", "database") + ';'

		""" Check if we are using trusted connection """
		if connection_file.get("ConnectionString", "trusted") != 'yes':
			connection_string += "UID=" + connection_file.get("ConnectionString", "user") + ';'
			connection_string += "PWD=" + connection_file.get("ConnectionString", "password")
		else:
			connection_string += "Trusted_Connection=yes;"

		return connection_string

	def is_reachable(self):
		""" Check data source is reachable """
		if self.source_type == self.TYPE_DATABASE:
			connection_string = self._build_connection_string()
			print("Connection string " + connection_string)
			try:
				cnxn = pyodbc.connect(connection_string)
				cnxn.close()
				return 1
			except Exception as e:
				print("Error :: is_reachable :: " + str(e))
				return 0
		elif self.source_type == self.TYPE_FILE:
			#Load from provided path
			return 1
		elif self.source_type == self.TYPE_WEB:
			#Load from provided url
			return 1
		else:
			return 0

	def logEvent(self, event_description, member_id):
		""" Loads configuration for specified clientId and returns it as an object """
		if self.source_type == self.TYPE_DATABASE:
			connection_string = self._build_connection_string()
			try:
				cnxn = pyodbc.connect(connection_string)
				cursor = cnxn.cursor()
				cursor.execute('INSERT INTO [dbo].[History]	([MemberId],[EventDescription]) VALUES (' + str(member_id) + ',\'' + str(event_description) + '\')')
				cnxn.commit()
				"""

				"""
			except Exception as e:
				print("Error :: logEvent :: " + str(e))
			finally:
				#Cleaning up
				cursor.close()
				del cursor
				cnxn.close()
		elif self.source_type == self.TYPE_FILE:
			#Load from provided path
			print("Write to file")
		elif self.source_type == self.TYPE_WEB:
			#Load from provided url
			print("Send to URL")

	def get_member_associated_to_credential(self, credential):
		if self.source_type == self.TYPE_DATABASE:
			connection_string = self._build_connection_string()
			try:
				cnxn = pyodbc.connect(connection_string)
				cursor = cnxn.cursor()
				""" Get member id associated to provided token """
				cursor.execute('SELECT TOP 1 MemberId FROM CredentialMember WHERE Token =' + str(credential))
				row = cursor.fetchone()
				if row is not None:
					""" Get member associated to previsouly found id """
					cursor.execute('SELECT TOP 1 MemberId, Name, LastName FROM Member WHERE MemberId =' + str(row[0]))
					row = cursor.fetchone()
					if row is not None:
						#Cleaning up
						if 'cursor' in locals():
							cursor.close()
							del cursor
						return row[0], str(row[1]) + " " + str(row[2])
			except Exception as e:
				print("Error :: get_member_associated_to_credential :: " + str(e))
			""" In case of error or not found """
			#Cleaning up
			if 'cursor' in locals():
				cursor.close()
				del cursor
			return


	def get_or_create_client_access_rights(self, card_id, zone_id):
		""" Load access rights for specified client / zone """
		can_access = False
		if self.source_type == self.TYPE_DATABASE:
			connection_string = self._build_connection_string()
			try:
				cnxn = pyodbc.connect(connection_string)
				cursor = cnxn.cursor()

				m_id, m_name = self.get_member_associated_to_credential(card_id)

				if m_id is not None:
					""" This card is registered, get access rights """
					member_id = m_id
					member_name = m_name
					cursor.execute('SELECT TOP 1 GroupId FROM GroupMember WHERE MemberId =' + str(member_id))
					row = cursor.fetchone()

					if row is not None:
						""" This member is associated to a groupe """
						group_id = row[0]
						cursor.execute('SELECT TOP 1 CanAccess FROM ZoneAccess WHERE GroupId =' + str(group_id) + 'AND ZoneId =' + str(zone_id))
						row = cursor.fetchone()
						if row is not None:
							""" Get access result """
							can_access = row[0]
							if can_access == True:
								self.logEvent(member_name + " marco en la zona " + str(zone_id) + ", autorizado", member_id)
							else:
								self.logEvent(member_name + " marco en la zona " + str(zone_id) + ", no autorizado", member_id)
				else:
					""" This card is not registered, create new member """
					cursor.execute('INSERT INTO Member(CardId) VALUES (' + str(card_id) + ')' )
					cursor.execute('INSERT INTO CredentialMember(Token) VALUES (' + str(card_id) + ')' )
					cnxn.commit()
					cursor.execute('SELECT TOP 1 MemberId FROM Member WHERE CardId =' + str(card_id))
					""" Retrieve memberId """
					row = cursor.fetchone()
					member_id = row[0]
					""" Insert default group """
					cursor.execute('INSERT INTO GroupMember(GroupId, MemberId) VALUES (1,' + str(member_id) + ')')
					cnxn.commit()
					""" By default, deny access """
					can_access = False
			except Exception as e:
				print("Error :: get_or_create_client_access_rights :: " + str(e))
			finally:
				#Cleaning up
				if 'cursor' in locals():
					cursor.close()
					del cursor

				cnxn.close()
		else:
			print("Not implemented")

		return can_access

	def update_member_info(self, member):
		assert(isinstance(member, Member))
		connection_string = self._build_connection_string()

		try:
			cnxn = pyodbc.connect(connection_string)
			cursor = cnxn.cursor()
			""" Update user info and get it out of 'Default' group """
			cursor.execute('UPDATE AccessControl.dbo.Member SET Name=\''+ member.firstname + '\',LastName=\'' + member.lastname + '\' WHERE MemberId = ' + member.id)
			cursor.execute('UPDATE AccessControl.dbo.GroupMember SET GroupId='+ member.groupId +' WHERE MemberId = ' + member.id)

			cnxn.commit()
		except Exception as e:
			print("Error :: update_member_info :: " + str(e))
			pass
		finally:
			cnxn.close()

	def get_members_groups(self):
		groups = []
		connection_string = self._build_connection_string()
		try:
			cnxn = pyodbc.connect(connection_string)
			cursor = cnxn.cursor()
			cursor.execute('SELECT TOP 100 GroupId,Description FROM AccessControl.dbo.[Group]')

			"""
				Return the list of available groups
			"""

			for row in cursor.fetchall():
				group = Group(row[0], row[1])
				groups.append(group)
		except Exception as e:
			print("Error :: get_members_groups :: " + str(e))
		finally:
			if 'cursor' in locals():
				#Cleaning up
				cursor.close()
				del cursor
			cnxn.close()

		return groups

	def get_not_enrolled_members(self):
		not_enrolled_ids = []
		connection_string = self._build_connection_string()
		try:
			cnxn = pyodbc.connect(connection_string)
			cursor = cnxn.cursor()
			cursor.execute('SELECT TOP 100 MemberId, CardId FROM AccessControl.dbo.viewNotEnrolledMembersId')

			"""
				Return the list of not enrolled users
			"""

			for row in cursor.fetchall():
				member = Member(row[0])
				member.token = str(row[1])
				not_enrolled_ids.append(member)
		except Exception as e:
			print("Error :: get_not_enrolled_members :: " + str(e))
		finally:
			if 'cursor' in locals():
				#Cleaning up
				cursor.close()
				del cursor
			cnxn.close()

		return not_enrolled_ids

	def load_device_configuration(self, client_id):
		""" Loads configuration for specified clientId and returns it as an object """
		config = DeviceConfiguration(client_id)
		if self.source_type == self.TYPE_DATABASE:
			connection_string = self._build_connection_string()
			try:
				cnxn = pyodbc.connect(connection_string)
				cursor = cnxn.cursor()
				cursor.execute('SELECT TOP 1 ZoneId, Enabled, ControllerTypeId, ControllerDescription FROM AccessControl.dbo.Controller WHERE ControllerCode =' + str(client_id))

				row = cursor.fetchone()

				#Bind to actual configuration object
				if row is not None:
					config.zone = row[0]
					config.enabled = row[1]
					config.deviceType = row[2]
					config.description = row[3]
				else:
					print("No configuration found for client " +  str(client_id))
			except Exception as e:
				print("Error :: load_device_configuration :: " + str(e))
			finally:
				#Cleaning up
				cursor.close()
				del cursor
				cnxn.close()

			return config
		elif self.source_type == self.TYPE_FILE:
			#Load from provided path
			print("From file")
		elif self.source_type == self.TYPE_WEB:
			#Load from provided url
			print("From URL")
