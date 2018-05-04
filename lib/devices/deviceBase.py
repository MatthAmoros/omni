__all__ = ['DeviceBase']
__version__ = '0.1'


from threading import Thread
from time import sleep

class DeviceBase(object):
	
	def __init__(self, name):
		self.VERSION = "0.0.1"	
		self.name = str(name)
		self.type = "NONE"
		
		self.master_url = ''
		self.master_secret = ''
		
		self.is_configuration_loaded = False
		self.is_zone_enabled = False
		self.is_running = False
		self.must_stop = False

	def run(self):
		""" Starts device main loop """
		device_loop_thread = Thread(target=self.main_loop)
		#Start thread
		device_loop_thread.start();
		
		print("Device " + str(self.name) + " started")

		device_loop_thread.join()
		
	def unload_device(self):
		""" Unload device and instanciate an empty one"""
		self.stop_loop()
		self = DeviceBase(self.name)
	
	def main_loop(self):
		raise NotImplementedError('DeviceBase must be inherited')
		
	def stop_loop(self):
		raise NotImplementedError('DeviceBase must be inherited')
