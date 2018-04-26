from threading import Thread
from time import sleep

class DeviceBase(object):
	mustStop = 0
	
	def __init__(self, name):
		self.VERSION = "0.0.1"	
		self.name = str(name)
		self.type = "NONE"
		self.masterUrl = ''
		self.masterSecret = ''
		self.configurationLoaded = 0
		self.zoneEnabled = 0
		self.isRunning = False

	def run(self):
		""" Starts device main loop """
		deviceLoop = Thread(target=self.mainLoop)
		#Start thread
		deviceLoop.start();
		
		print "Device " + str(self.name) + " started"

		deviceLoop.join()
		
	def unloadDevice(self):
		""" Unload device and instanciate an empty one"""
		self.stopLoop()
		self = DeviceBase(self.name)
	
	def mainLoop(self):
		raise NotImplementedError('DeviceBase must be inherited')
		
	def stopLoop(self):
		raise NotImplementedError('DeviceBase must be inherited')
