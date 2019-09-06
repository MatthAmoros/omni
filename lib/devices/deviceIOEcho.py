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
		DeviceBase.type = "IOEcho"
		if is_running_on_pi == True:
			print("Starting IOEcho device.")

			"""
				Set pin numbering mode
			"""
			GPIO.setmode(GPIO.BCM)

			"""
				TODO : Add dynamic configuration, or stroe pin map in a file
			"""
			self.pin_and_label_matrix = [
				{'pin': 2, 'label': 'S011'},
				{'pin': 3, 'label': 'S012'},
				{'pin': 4, 'label': 'S033'},
				{'pin': 14, 'label': 'S021'},
				{'pin': 15, 'label': 'S022'},
				{'pin': 18, 'label': 'S023'},
				{'pin': 10, 'label': 'S031'},
				{'pin': 9, 'label': 'S032'},
				{'pin': 11, 'label': 'S033'}
			]

			for pin_and_label in self.pin_and_label_matrix:
				GPIO.setup(pin_and_label['pin'], GPIO.IN)
				GPIO.add_event_detect(pin_and_label['pin'], GPIO.RISING, callback=self._on_data_received)
				print("Pin " + str(pin_and_label['pin']) + " initialized as input.")

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
				for pin_and_label in self.pin_and_label_matrix:
					if pin_and_label['pin'] == gpio:
						self.echo_signal_to_target(pin_and_label['label'])
			except RuntimeError:
				pass

	def echo_signal_to_target(self, signal):
		print("Sending " + str(signal) + " signal to target")
		sleep(0.2)

	#Overrided from DeviceBase
	def stop_loop(self):
		if is_running_on_pi == True:
			GPIO.cleanup()

		self.must_stop = True
