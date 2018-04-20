class DeviceFactory:
	def __init__(self):
		return
	
	def getDevice(self, deviceType):
		if deviceType == 1:
			return DeviceHIDReader()
		elif deviceType == 2:
			raise NotImplementedError("Device type 2 not implemented")
