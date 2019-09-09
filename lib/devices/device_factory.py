"""
	DeviceFactory, returns device according to passed type
"""
__all__ = ['DeviceFactory']
__version__ = '0.1'

import platform


from lib.devices.device_HIDReader import HIDReader
from lib.devices.device_IOEcho import IOEcho
from lib.devices.device_ZK45FingerPrintReader import ZK45Reader
from lib.devices.device_ZFM20FingerPrintReader import ZFM20Reader
from lib.devices.device_base import DeviceBase
from lib.common import PrintColor
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
			device.master_url = self.master_url
			r = requests.get(self.master_url + '/configuration/' + self.name)

			if r.status_code == 200:
				try:
					#Request success
					config = json.loads(r.text)
					if config['deviceType'] == 1:
						""" HID Reader """
						device = HIDReader(self.name)
					if config['deviceType'] == 2:
						""" ZK45Reader """
						device = ZK45Reader(self.name)
					if config['deviceType'] == 4:
						""" ZFM20Reader """
						device = ZFM20Reader(self.name)
					if config['deviceType'] == 5:
						""" IOEcho """
						device = IOEcho(name=self.name, pin_and_label_matrix='', target_address='192.168.2.54', target_port=900)
					elif config['deviceType'] == 0:
						""" None """
						device = DeviceBase(name=self.name)
					else:
						""" Disable """
						device = DeviceBase(self.name)

					device.zone_id = config['zone']

					device.is_zone_enabled = config['enabled']
					device.is_zone_day_time_only = config['dayTimeOnly']
					device.is_configuration_loaded = True

					device.master_secret = config['secret']
					device.master_url = self.master_url

					device.is_in_error = False
					device.error_status = "OK"
					device.type = config['deviceType']

					print(PrintColor.OKBLUE + "Configuration loaded.")
				except Exception as e:
					error_message = "Device type not supported by current platform. Configuration aborted. (" + str(e) + ")"
					print(PrintColor.FAIL + error_message)
					device.zone_id = 1

					device.is_zone_enabled = False
					device.is_zone_day_time_only = False
					device.is_in_error = True
					device.error_status = error_message
			else:
				print("Configuration loading failed. (Server response : " + str(r.status_code) + ")")
				device.zone_id = 1
				device.is_zone_enabled = False
				device.is_zone_day_time_only = False
				device.is_in_error = True
				device.error_status = "Configuration loading failed. (Server response : " + str(r.status_code) + ")"
		else:
			self.zone_id = 1
			self.is_zone_enabled = True
			self.is_zone_day_time_only = True
			device.is_in_error = True
			device.error_status = "No master URL defined"

		device.report_state()
		return device

	def set_master(self, master_url):
		""" Sets default master """
		if(not master_url.startswith("http")):
			print(PrintColor.FAIL + "Error, master is not a valid URL")

		if master_url.endswith('/'):
			master_url = master_url[:-1] #Remove last '/'

		r = requests.get(master_url + '/confirmAdopt/' + str(self.name))
		if r.status_code == 200:
			print(PrintColor.OKBLUE + "Setting master URL to " + master_url)
			self.master_url = master_url
		else:
			print(PrintColor.FAIL + "Error, invalid master response (" + str(r.status_code) + ")")
