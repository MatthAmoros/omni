"""
This class is shared between clients and servers to exchange
configuration information. They are not meant to have any logics,
but formalize a common interface.
"""
__all__ = ['DeviceConfiguration', 'DeviceStatus', 'Member', 'ServerSetting']
__version__ = '0.1'

class DeviceConfiguration:
	zone = 0 #Zone Id that identify door controller location
	enabled = 0 #Controller enabled ?
	day_time_only = 0 #Only enabled on day time ?
	authorize_only = "" #If empty, authorize all, else groups with ';' separators
	client_id = 0 #Client ID
	secret = "" #Server secret, for future cryptographic uses
	deviceType = 0
	description = ""

	def __init__(self, client_id):
		self.client_id = client_id

	def __str___(self):
		return "Configuration : " + str(description) + " Zone : " + str(self.zone) + " Enabled : " + str(self.enabled) + " DayTimeOnly : " + str(self.day_time_only) + " AuthorizeOnly : " + str(self.authorize_only + " DeviceType : " + str(self.deviceTpe))

	def serialize(self):
		"""Serializes current object instance (used with jsonify)"""
		return { 'description': self.description, 'zone' : self.zone, 'enabled' : self.enabled, 'dayTimeOnly' : self.day_time_only, 'authorizeOnly' : self.authorize_only, 'secret' : self.secret, 'deviceType' : self.deviceType}

class DeviceStatus:
	client_id = 0
	is_in_error = False
	error_status = ""

	def __init__(self, client_id, in_error, error_status):
		self.client_id = client_id
		self.is_in_error = in_error
		self.error_status = error_status

	def serialize(self):
		"""Serializes current object instance (used with jsonify)"""
		return { 'client_id': self.client_id, 'is_in_error' : self.is_in_error, 'error_status' : self.error_status }

class Member:
	token = ''
	name = ''
	lastname = ''
	groupId = 1

	def __init__(self, id):
		self.id = id
		self.token = ''
		self.name = ''
		self.lastname = ''

	def __str___(self):
		return "Member : " + str(self.id) + " | " + str(self.token) + " | " + str(self.name) + " | " + str(self.lastname)

class Group:
	id = 0
	name = ''

	def __init__(self, id, name):
		self.id = id
		self.name = name

	def __str___(self):
		return "Group : " + str(self.id) + " | " + str(self.name) + " | "

class ServerSetting:
	def __init__(self, settingType):
		self.type = settingType
		self.parameters = []

	def __str___(self):
		return "Setting : " + str(self.type) + " | " + str(self.parameters)

	def serialize(self):
		"""Serializes current object instance (used with jsonify)"""
		return { 'type': self.type, 'parameters' : self.parameters}
