"""
	IOEcho device, receive GPIO, send them thought TCP to target
"""

__all__ = ['IOEcho']
__version__ = '0.1'

from .deviceBase import DeviceBase
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

class IOEcho(DeviceBase):
	def __init__(self, name, pin_and_label_matrix):
		DeviceBase.__init__(self, name)

		self.pin_and_label_matrix = pin_and_label_matrix

		for pin_and_label in self.pin_and_label_matrix:
			GPIO.setup(pin_and_label['pin'], GPIO.IN)
			GPIO.add_event_detect(pin_and_label['pin'], GPIO.RISING, callback=self._on_data_received)
		"""
			Set action gpio to 0V
		"""
		GPIO.setmode(GPIO.BCM)

		"""
			Blink to show loaded
		"""
		print("IOEcho device built !")

	#Overrided from DeviceBase
	def main_loop(self):
		""" Starts RFID reading loop """
		try:
			print("Starting controller...")
			if is_running_on_pi == True:
				while self.must_stop == False :
					if self.is_zone_enabled == True:
						self.is_running = True
						""" Controller is enable, start reading """
						#Prevent over-header
						sleep(1)

					else:
						""" Controller is disable, wait for a valid configuration """
						break
		finally:
			print("Reading loop stopped")

		sleep(1)

	def _on_data_received(self, gpio):
		if is_running_on_pi == True:
			try:
				""" Send GPIO signal to open the door """
				self.echo_signal_to_target(self.pin_and_label[gpio]['label'])
			except RuntimeError:
				pass

	def echo_signal_to_target(self):
		print("Sending signal to target")

	#Overrided from DeviceBase
	def stop_loop(self):
		if is_running_on_pi == True:
			GPIO.cleanup()

		self.must_stop = True