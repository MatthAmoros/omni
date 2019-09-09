"""
	IOEcho device, receive GPIO, send them thought TCP to target
"""

__all__ = ['IOEcho']
__version__ = '0.1'

from lib.devices.device_base import DeviceBase
from time import sleep
from lib.common import PrintColor
import requests
import json
from socket import *

try:
	import RPi.GPIO as GPIO
	is_running_on_pi = True
except RuntimeError:
	print(PrintColor.WARNING + "Starting without GPIO")
	is_running_on_pi = False
	pass

class IOEcho(DeviceBase):
	pin_and_label_matrix = ''
	def __init__(self, name, pin_and_label_matrix, target_address='', target_port=9100):
		DeviceBase.__init__(self, name)
		DeviceBase.type = "IOEcho"
		if is_running_on_pi == True:
			print(PrintColor.OKBLUE + "Starting IOEcho device...")
			self.target_address = target_address
			self.target_port = target_port

			"""
				Set pin numbering mode
			"""
			GPIO.setmode(GPIO.BOARD)

			"""
				TODO : Add dynamic configuration, or stroe pin map in a file
			"""
			self.pin_and_label_matrix = [
				{'pin': 3, 'label': 'S011', 'value': 1},
				{'pin': 5, 'label': 'S012', 'value': 1},
				{'pin': 7, 'label': 'S013', 'value': 1},
				{'pin': 11, 'label': 'S021', 'value': 1},
				{'pin': 13, 'label': 'S022', 'value': 1},
				{'pin': 15, 'label': 'S023', 'value': 1},
				{'pin': 19, 'label': 'S031', 'value': 1},
				{'pin': 21, 'label': 'S032', 'value': 1},
				{'pin': 23, 'label': 'S033', 'value': 1}
			]

			for pin_and_label in self.pin_and_label_matrix:
				""" Should add a physical pull up """
				GPIO.setup(pin_and_label['pin'], GPIO.IN)
				""" Set falling edge detection, callback and debounce time to 300 ms """
				GPIO.add_event_detect(pin_and_label['pin'], GPIO.FALLING, callback=self._on_data_received, bouncetime=300)
				print(PrintColor.OKBLUE + "Pin " + str(pin_and_label['pin']) + " initialized as input.")

			self.pre_start_diagnose()

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
			else:
				print(PrintColor.WARNING + "This device can only work with GPIO, canceling ...")
				self.is_in_error = True
				sleep(5)
		finally:
			print("Reading loop stopped")

	def pre_start_diagnose(self):
		for pin_and_label in self.pin_and_label_matrix:
			if pin_and_label['value'] != GPIO.input(pin_and_label['pin']):
				print(str(PrintColor.WARNING) +  "[W] Pin " + str(pin_and_label['pin']) + " is not set to initialization value.")

	#Overrided from DeviceBase
	def get_status(self):
		for pin_and_label in self.pin_and_label_matrix:
			pin_and_label['value'] = GPIO.input(pin_and_label['pin'])

		return str(self.pin_and_label_matrix)

	def _on_data_received(self, gpio):
		if is_running_on_pi == True:
			try:
				""" Send GPIO signal to open the door """
				for pin_and_label in self.pin_and_label_matrix:
					if pin_and_label['pin'] == gpio:
						self.echo_signal_to_target(pin_and_label['label'])
						break
			except RuntimeError:
				pass

	def echo_signal_to_target(self, signal):
		print(PrintColor.OKBLUE + "Sending " + str(signal) + " signal to " + str(self.target_address) + ":" + str(self.target_port))
		client_socket = socket(AF_INET, SOCK_STREAM)
		client_socket.connect((self.target_address, self.target_port))
		client_socket.sendall(bytes(str(signal).encode('utf-8')))
		client_socket.close()

	#Overrided from DeviceBase
	def stop_loop(self):
		if is_running_on_pi == True:
			GPIO.cleanup()

		self.must_stop = True
