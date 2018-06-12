__all__ = ['DeviceBase']
__version__ = '0.1'


from threading import Thread
from time import sleep
import requests

class DeviceBase(object):

	def __init__(self, name):
		self.VERSION = "0.0.1"
		self.name = str(name)
		self.client_id = str(name)
		self.endpoint = ""
		self.type = "NONE"

		self.master_url = ''
		self.master_secret = ''
		self.error_status = ""

		self.is_configuration_loaded = False
		self.is_zone_enabled = False
		self.is_running = False
		self.is_in_error = False
		self.must_stop = False

	def __str__(self):
		return "Zone enabled " + str(self.is_zone_enabled) + " | Running " + str(self.is_running) + " | Configuration loaded " + str(self.is_configuration_loaded) + " | Must stop " + str(self.must_stop)

	def run(self):
		""" Starts device main loop """
		device_loop_thread = Thread(target=self.main_loop)

		#Pre start state
		self.report_state()

		#Start thread
		device_loop_thread.start();

		print("Device " + str(self.name) + " started")

		device_loop_thread.join()

	def unload_device(self):
		""" Unload device and instanciate an empty one"""
		self.stop_loop()
		self = DeviceBase(self.name)

	def report_state(self):
		if len(self.master_url) > 0:
			r = requests.post(self.master_url + '/report/state', json={"client_id": str(self.client_id), "is_in_error" : str(self.is_in_error), "error_status" : str(self.error_status) })
			if str(r.status_code) == "200":
				print("Successfully reported status [" + str(self.error_status) + "] to server")
			else:
				print("An error ocurred while reporting status : (server response " + str(r.status_code) + ")")
		else:
			print("Abort reporting, master not set.")

	def main_loop(self):
		raise NotImplementedError('main_loop must be overloaded')

	def stop_loop(self):
		raise NotImplementedError('main_loop must be overloaded')
