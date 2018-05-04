""" 
	HIDReader device, using MFRC522 controller
"""

__all__ = ['HIDReader']
__version__ = '0.1'

from .deviceBase import DeviceBase
from time import sleep
import requests
import json

try:
	import RPi.GPIO as GPIO
	from .SimpleMFRC522 import SimpleMFRC522 as SimpleMFRC522 #Credit to Simon Monk https://github.com/simonmonk/
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
			if is_running_on_pi == True:		
				reader = SimpleMFRC522()
				
			print("Starting controller...")
			
			while self.must_stop == False :
				if self.is_zone_enabled == True:
					self.is_running = True
					""" Controller is enable, start reading """
					if is_running_on_pi == True:
						id, text = reader.read_no_block()
						print(str(id))
					else:
						sleep(0.5)
						id = 22554655721354687
						text = "hashedIdAndMasterSecret"
						
					""" If we read something """
					if id != None:
						result = self.validate_credential(id, text)
						if result == 1:
							print(str(id) + " valid !")
							
							if is_running_on_pi == True:
								try:
									""" Send GPIO signal to open the door """
									GPIO.output(12, GPIO.HIGH)
									sleep(0.3)
									GPIO.output(12, GPIO.LOW)
								except RuntimeError:
									pass
									
						else:
							print(str(id) + " error !")
							
					""" Read every 200ms """
					sleep(0.2)				
				else:
					""" Controller is disable, wait for a valid configuration """
					break
		finally:
			print("Reading loop stopped")

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
