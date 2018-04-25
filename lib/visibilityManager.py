from socket import *
class VisibilityManager:	
	
	def __init__(self):
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.mustStop = False
		self.DISCOVERY_MESSAGE = str("42 !")
		
	def sendDiscoveryDatagram(self):
		""" Broadcast a message to tell the world your are here ... """
		self.socket
		self.socket.sendto(self.DISCOVERY_MESSAGE, ('255.255.255.255', 54545))
	
	def listenForDiscoveryDatagram(self):
		# Bind the socket to the port
		server_address = ('localhost', 54545)
		self.socket.bind(server_address)
		self.socket.settimeout(1)
		print "Starting up discovery on port 54545"

		while self.mustStop == False:			
			try:
				data, address = self.socket.recvfrom(4096)
				print str(data)
				if data == self.DISCOVERY_MESSAGE:
					""" Client found """
					print "Client found at " + str(address)
					return address
			except KeyboardInterrupt:
				break;
			except:
				pass
		
		print "Shutting down discovery"
		self.socket.close()
