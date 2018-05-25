"""
	VisibilityManager, operate a socket to send or listen for specific UDP packet
	Stray clients call 'send_discovery_datagram' to broadcast an UDP message.
	Servers listen with 'listen_for_discovery_datagram' for the same message and adopt captured clients
"""
__all__ = ['DeviceFactory']
__version__ = '0.1'

from socket import *
import requests

class VisibilityManager:

	def __init__(self):
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.mustStop = False
		self.DISCOVERY_MESSAGE = bytes(str("42 !").encode('utf-8'))

	def send_discovery_datagram(self, port=54545):
		""" Broadcast a message to tell the world your are here ... """
		self.socket.sendto(self.DISCOVERY_MESSAGE, ('255.255.255.255', port))

	def listen_for_discovery_datagram(self, port=54545):
		# Bind the socket to the port
		server_address = ('0.0.0.0', port)
		self.socket.bind(server_address)
		self.socket.settimeout(1)
		print("Starting up discovery on port " + str(port))

		while self.mustStop == False:
			try:
				data, address = self.socket.recvfrom(4096)

				if data == self.DISCOVERY_MESSAGE:
					""" Client found """
					client_adoption_endpoint = 'http://' + str(address[0]) + ':5555/adopt'
					print("Client found at " + str(client_adoption_endpoint))

					try:
						r = requests.post(client_adoption_endpoint, data = {'master':''})
					except requests.exceptions.ConnectionError:
						print("Connection timed out with client endpoint " + str(client_adoption_endpoint))

			except KeyboardInterrupt:
				break;
			except timeout:
				pass;

		print("Shutting down discovery")
		self.socket.close()
