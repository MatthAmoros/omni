"""
	DeviceFactory, returns device according to passed type
"""
__all__ = ['DeviceFactory']
__version__ = '0.1'

import platform

proc = platform.processor()
if proc == "ARM":
	""" Loading RaspberryPi only devices """
	from .deviceHIDReader import HIDReader

from .deviceFingerPrintReader import FingerPrintReader
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
				try:
					#Request success
					config = json.loads(r.text)
					if config['deviceType'] == 1:
						""" HID Reader """
						device = HIDReader(self.name)
					if config['deviceType'] == 2:
						""" FingerPrint Reader """
						device = FingerPrintReader(self.name)
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
				except NameError:
					print("Device type not supported by current platform. Configuration aborted.")
					device.zone_id = 1
					device.is_zone_enabled = False
					device.is_zone_day_time_only = False
				finally:
					return device
			else:
				print("Configuration loading failed. (Server response : " + str(r.status_code) + ")")
				device.zone_id = 1
				device.is_zone_enabled = False
				device.is_zone_day_time_only = False
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
		else:
			print("Error, invalid master response")
