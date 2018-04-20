from deviceBase import DeviceBase
import RPi.GPIO
import SimpleMFRC522 as SimpleMFRC522 #Credit to 
""" Setting output GPIO """
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
	
class HIDReader(DeviceBase):
	def mainLoop():
	""" Starts RFID reading loop """
	try:
		if mockReader == 0:		
			reader = SimpleMFRC522.SimpleMFRC522()
		print "Starting controller..."
		while mustStop == 0 :
			if doorCtrl.zoneEnabled == 1:	
				""" Controller is enable, start reading """
				if mockReader == 0:
					id, text = reader.read()
				else:
					sleep(0.5)
					id = 22554655721354687
					text = "hashedIdAndMasterSecret"
					
				result = doorCtrl.validateCredential(id, text)
				
				if result == 1:
					print str(id) + " valid !"
					if runningOnPi == 1:
						""" Send GPIO signal to open the door """
						GPIO.output(12, GPIO.HIGH)
						sleep(0.3)
						GPIO.output(12, GPIO.LOW)
				else:
					print str(id) + " error !"
			else:
				""" Controller is disable, wait for a valid configuration """
				sleep(1)
	except KeyboardInterrupt:
		pass		
	finally:
		print "Reader stopped"
		if mockReader == 0:
			GPIO.cleanup()

	print "Gracefully closed"
	sleep(1)
		
	def stopLoop(self):
		GPIO.cleanup()
