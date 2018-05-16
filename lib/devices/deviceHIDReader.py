"""
	HIDReader device, using MFRC522 controller
"""

__all__ = ['HIDReader']
__version__ = '0.1'

from deviceBase import DeviceBase
from protocols.wiegand import WiegandReader
from time import sleep
import requests
import json


try:
	import RPi.GPIO as GPIO
	is_running_on_pi = True
except RuntimeError:
	print("Starting without GPIO")
	is_running_on_pi = False
	pass

class HIDReader(DeviceBase):
	def __init__(self, name):
		DeviceBase.__init__(self, name)
		print("HID Reader built !")

	def main_loop(self):
		""" Starts RFID reading loop """
		try:
			print("Starting controller...")
			GPIO.setup(23, GPIO.OUT)

			with WiegandReader(GPIO, 14, 15, self._on_data_read) as wiegand_reader:
				while self.must_stop == False :
					if self.is_zone_enabled == True:
						self.is_running = True
						""" Controller is enable, start reading """
						if is_running_on_pi == True:
							sleep(0.3)
							""" Waiting for callback interupt """
						else:
							sleep(0.5)
							id = 22554655721354687
							text = "hashedIdAndMasterSecret"

					else:
						""" Controller is disable, wait for a valid configuration """
						break
		finally:
			print("Reading loop stopped")
			wiegand_reader.cancel()

		sleep(1)

	def _on_data_read(bits, value):
		if bits > 0:
			result = self.validate_credential(str(value), 'CARD')
			if result == 1:
				print(str(value) + " valid !")
				if is_running_on_pi == True:
					try:
						""" Send GPIO signal to open the door """
						GPIO.output(23, GPIO.HIGH)
						sleep(0.3)
						GPIO.output(23, GPIO.LOW)
					except RuntimeError:
						pass
			else:
				print(str(value) + " error !")

	def stop_loop(self):
		if is_running_on_pi == True:
			GPIO.cleanup()

		self.must_stop = True

	def validate_credential(self, card_id, secret):
		""" Validates provided credentials against master's db """
		if not self.is_configuration_loaded:
			print("No configuration loaded")
			return -1

		if len(self.master_url) > 0:
			print("Getting " + self.master_url + '/accessRule/' + str(self.zone_id) + '/' + str(card_id))
			try:
				r = requests.get(self.master_url + '/accessRule/' + str(self.zone_id) + '/' + str(card_id))
				if r.status_code == 200:
					return 1
				else:
					return -1
			except requests.ConnectionError:
				""" Server cannot be joined, might be a network issue, try again next time
					For now, return invalid card flag
				 """
				if self.retry < 10:
					self.retry += 1
					return -1
				else:
					""" Server cannot be joined, let's try to forget master and reset client """
					self.unload_deviceevice()
		else:
			print("Master URL not set. (" + self.master_url + ")")
			return -1
