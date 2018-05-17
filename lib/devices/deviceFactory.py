"""
	DeviceFactory, returns device according to passed type
"""
__all__ = ['DeviceFactory']
__version__ = '0.1'

from .deviceHIDReader import HIDReader
from .deviceBase import DeviceBase
import requests
import json

class DeviceFactory:
	def __init__(self, name):
		self.VERSION = "0.0.1"
		self.name = str(name)
		self.type = "NONE"
		self.master_url = ''
		self.master_secret = ''
		self.is_configuration_loaded = True
		self.is_zone_enabled = True
		self.isRunning = False
		return

	def get_configuration(self):
		""" Asks master for configuration """
		device = DeviceBase(self.name)

		if len(self.master_url) > 0:
			r = requests.get(self.master_url + '/configuration/' + self.name)

			if r.status_code == 200:
				#Request success
				config = json.loads(r.text)
				if config['deviceType'] == 1:
					""" HID Reader """
					device = HIDReader(self.name)
				elif config['deviceType'] == 0:
					""" None """
					device = DeviceBase(self.name)
				else:
					""" Disable """
					device = DeviceBase(self.name)

				device.zone_id = config['zone']

				device.is_zone_enabled = config['enabled']
				device.is_zone_day_time_only = config['dayTimeOnly']
				device.is_configuration_loaded = True

				device.master_secret = config['secret']
				device.master_url = self.master_url

				print("Configuration loaded.")

				return device
			else:
				print("Configuration loading failed.")
				self.zone_id = 1
				self.is_zone_enabled = False
				self.is_zone_day_time_only = False
				return device
		else:
			self.zone_id = 1
			self.is_zone_enabled = True
			self.is_zone_day_time_only = True
			return device

	def set_master(self, master_url):
		""" Sets default master """
		if(not master_url.startswith("http")):
			print("Error, master is not a valid URL")

		if master_url.endswith('/'):
			master_url = master_url[:-1] #Remove last '/'

		r = requests.get(master_url + '/confirmAdopt/' + str(self.name))
		if r.status_code == 200:
			print("Setting master URL to " + master_url)
			self.master_url = master_url
			self.get_configuration()
		else:
			print("Error, invalid master response")
