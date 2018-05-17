"""
	HIDReader device, using MFRC522 controller
"""

__all__ = ['HIDReader']
__version__ = '0.1'

from .deviceBase import DeviceBase
from .protocols.wiegand import WiegandReader
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
	def __init__(self, name, action_pin_BCM=23, led_pin_BCM=23, data0_pin_BCM=14, data1_pin_BCM=15):
		DeviceBase.__init__(self, name)

		self._data0_pin_BCM = data0_pin_BCM
		self._data1_pin_BCM = data1_pin_BCM
		self._led_pin_BCM = led_pin_BCM
		self._action_pin_BCM = action_pin_BCM
		"""
			Set action gpio to 0V
		"""
		GPIO.setmode(GPIO.BCM)
		if self._action_pin_BCM != self._led_pin_BCM:
			GPIO.setup(self._action_pin_BCM, GPIO.OUT)
			GPIO.setup(self._action_pin_BCM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

		GPIO.setup(self._led_pin_BCM, GPIO.OUT)
		GPIO.setup(self._led_pin_BCM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

		"""
			Blink to show loaded
		"""
		self.blink_led()
		print("HID Reader built !")

	def main_loop(self):
		""" Starts RFID reading loop """
		try:
			print("Starting controller...")
			if is_running_on_pi == True:

				print("Setting up external vlaidation signal to BCM 23")
				with WiegandReader(GPIO, self._data0_pin_BCM, self._data1_pin_BCM, self._on_data_read) as wiegand_reader:
					print("Wiegand listener started")
					while self.must_stop == False :
						if self.is_zone_enabled == True:
							self.is_running = True
							""" Controller is enable, start reading """
							sleep(0.3)
							""" Waiting for callback interupt """
						else:
							""" Controller is disable, wait for a valid configuration """
							break
		finally:
			print("Reading loop stopped")
			if is_running_on_pi == True and wiegand_reader:
				wiegand_reader.cancel()

		sleep(1)

	def _on_data_read(self, bits, value):
		if bits > 0:
			result = self.validate_credential(str(value), 'CARD')
			if result == 1:
				if is_running_on_pi == True:
					try:
						""" Send GPIO signal to open the door """
						self.set_action_OK()
						print(str(value) + " valid !")
					except RuntimeError:
						pass
			else:
				print(str(value) + " error !")

	def blink_led(self):
		GPIO.output(self._led_pin_BCM, GPIO.HIGH)
		sleep(0.2)
		GPIO.output(self._led_pin_BCM, GPIO.LOW)
		sleep(0.2)
		GPIO.output(self._led_pin_BCM, GPIO.HIGH)
		sleep(0.2)
		GPIO.output(self._led_pin_BCM, GPIO.LOW)

	def set_action_OK (self):
		self.blink_led()
		GPIO.output(self._action_pin_BCM, GPIO.HIGH)
		sleep(1)

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
