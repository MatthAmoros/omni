from threading import Thread

class DeviceBase(object):
	mustStop = 0
    def run(self):
		""" Starts device main loop """
		#Delcare thread
		deviceLoop = Thread(target=self.mainLoop)
		#Start thread
		deviceLoop.start();

		try:
			while True :
				sleep(0.3)
		except KeyboardInterrupt:
			mustStop = 1
			pass
		
		print "Notify thread to stop..."
		self.stopLoop()
		sleep(1)
		#Join threads
		deviceLoop.join()
	
	def mainLoop(self):
		raise NotImplementedError('DeviceBase must be inherited')
		
	def stopLoop(self):
		raise NotImplementedError('DeviceBase must be inherited')
