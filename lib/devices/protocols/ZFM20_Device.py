import sys, os, serial
import struct
import time

"""
Initial work :
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

@author: Bastian Raschke <bastian.raschke@posteo.de>

Changes :
__enter__ / __exit__ / upload_image
enroll_user / match_fingerprint
@author: Matthieu AMOROS
"""

""" Converters """

def byteToString(byte):
	return struct.pack('@B', byte)

def stringToByte(string):
	return struct.unpack('@B', string)[0]

def shiftRight(n, x):
	""" shift n for x places """
	return (n >> x & 0xFF)

def shiftLeft(n, x):
	return (n << x)


## Start byte
FINGERPRINT_STARTCODE = 0xEF01

## Packet identification
##

FINGERPRINT_COMMANDPACKET = 0x01

FINGERPRINT_ACKPACKET = 0x07
FINGERPRINT_DATAPACKET = 0x02
FINGERPRINT_ENDDATAPACKET = 0x08

## Instruction codes
##

FINGERPRINT_VERIFYPASSWORD = 0x13
FINGERPRINT_SETPASSWORD = 0x12
FINGERPRINT_SETADDRESS = 0x15
FINGERPRINT_SETSYSTEMPARAMETER = 0x0E
FINGERPRINT_GETSYSTEMPARAMETERS = 0x0F
FINGERPRINT_TEMPLATEINDEX = 0x1F
FINGERPRINT_TEMPLATECOUNT = 0x1D

FINGERPRINT_READIMAGE = 0x01

## Note: The documentation mean upload to host computer.
FINGERPRINT_DOWNLOADIMAGE = 0x0A

FINGERPRINT_CONVERTIMAGE = 0x02

FINGERPRINT_CREATETEMPLATE = 0x05
FINGERPRINT_STORETEMPLATE = 0x06
FINGERPRINT_SEARCHTEMPLATE = 0x04
FINGERPRINT_LOADTEMPLATE = 0x07
FINGERPRINT_DELETETEMPLATE = 0x0C

FINGERPRINT_CLEARDATABASE = 0x0D

FINGERPRINT_COMPARECHARACTERISTICS = 0x03

## Note: The documentation mean download from host computer.
FINGERPRINT_UPLOADCHARACTERISTICS = 0x09

## Note: The documentation mean upload to host computer.
FINGERPRINT_DOWNLOADCHARACTERISTICS = 0x08

## Packet reply confirmations
##

FINGERPRINT_OK = 0x00
FINGERPRINT_ERROR_COMMUNICATION = 0x01

FINGERPRINT_ERROR_WRONGPASSWORD = 0x13

FINGERPRINT_ERROR_INVALIDREGISTER = 0x1A

FINGERPRINT_ERROR_NOFINGER = 0x02
FINGERPRINT_ERROR_READIMAGE = 0x03

FINGERPRINT_ERROR_MESSYIMAGE = 0x06
FINGERPRINT_ERROR_FEWFEATUREPOINTS = 0x07
FINGERPRINT_ERROR_INVALIDIMAGE = 0x15

FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH = 0x0A

FINGERPRINT_ERROR_INVALIDPOSITION = 0x0B
FINGERPRINT_ERROR_FLASH = 0x18

FINGERPRINT_ERROR_NOTEMPLATEFOUND = 0x09

FINGERPRINT_ERROR_LOADTEMPLATE = 0x0C

FINGERPRINT_ERROR_DELETETEMPLATE = 0x10

FINGERPRINT_ERROR_CLEARDATABASE = 0x11

FINGERPRINT_ERROR_NOTMATCHING = 0x08

FINGERPRINT_ERROR_DOWNLOADIMAGE = 0x0F
FINGERPRINT_ERROR_DOWNLOADCHARACTERISTICS = 0x0D

## Unknown error codes
##

FINGERPRINT_ADDRCODE = 0x20
FINGERPRINT_PASSVERIFY = 0x21

FINGERPRINT_PACKETRESPONSEFAIL = 0x0E

FINGERPRINT_ERROR_TIMEOUT = 0xFF
FINGERPRINT_ERROR_BADPACKET = 0xFE

## Constants
FINGERPRINT_ACCURACY_MINI_SCORE = 80

class ZFM20_Device(object):
	"""
	A python written library for the ZhianTec ZFM-20 fingerprint sensor.

	@attribute integer(4 bytes) __address
	Address to connect to sensor.

	@attribute integer(4 bytes) __password
	Password to connect to sensor.

	@attribute Serial __serial
	UART serial connection via PySerial.
	"""
	__address = None
	__password = None
	__serial = None

	def __init__(self, port = '/dev/ttyUSB0', baudRate = 57600, address = 0xFFFFFFFF, password = 0x00000000):
		"""
		Constructor

		@param string port
		@param integer baudRate
		@param integer(4 bytes) address
		@param integer(4 bytes) password
		"""

		if ( os.path.exists(port) == False ):
			raise ValueError('The fingerprint sensor port "' + port + '" was not found!')

		if ( baudRate < 9600 or baudRate > 115200 or baudRate % 9600 != 0 ):
			raise ValueError('The given baudrate is invalid!')

		if ( address < 0x00000000 or address > 0xFFFFFFFF ):
			raise ValueError('The given address is invalid!')

		if ( password < 0x00000000 or password > 0xFFFFFFFF ):
			raise ValueError('The given password is invalid!')

		self.__address = address
		self.__password = password

		## Initialize PySerial connection
		self.__serial = serial.Serial(port = port, baudrate = baudRate, bytesize = serial.EIGHTBITS, timeout = 2)

		if ( self.__serial.isOpen() == True ):
			self.__serial.close()

	def __enter__(self):
		self.__serial.open()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.__serial.close()

	def __del__(self):
		"""
		Destructor

		"""

		## Close connection if still established
		if ( self.__serial is not None and self.__serial.isOpen() == True ):
			self.__serial.close()

	def __writePacket(self, packetType, packetPayload):
		"""
		Send a packet to fingerprint sensor.

		@param integer(1 byte) packetType
		@param tuple packetPayload

		@return void
		"""

		## Write header (one byte at once)
		self.__serial.write(byteToString(shiftRight(FINGERPRINT_STARTCODE, 8)))
		self.__serial.write(byteToString(shiftRight(FINGERPRINT_STARTCODE, 0)))

		self.__serial.write(byteToString(shiftRight(self.__address, 24)))
		self.__serial.write(byteToString(shiftRight(self.__address, 16)))
		self.__serial.write(byteToString(shiftRight(self.__address, 8)))
		self.__serial.write(byteToString(shiftRight(self.__address, 0)))

		self.__serial.write(byteToString(packetType))

		## The packet length = package payload (n bytes) + checksum (2 bytes)
		packetLength = len(packetPayload) + 2

		self.__serial.write(byteToString(shiftRight(packetLength, 8)))
		self.__serial.write(byteToString(shiftRight(packetLength, 0)))

		## The packet checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
		packetChecksum = packetType + shiftRight(packetLength, 8) + shiftRight(packetLength, 0)

		## Write payload
		for i in range(0, len(packetPayload)):
			self.__serial.write(byteToString(packetPayload[i]))
			packetChecksum += packetPayload[i]

		## Write checksum (2 bytes)
		self.__serial.write(byteToString(shiftRight(packetChecksum, 8)))
		self.__serial.write(byteToString(shiftRight(packetChecksum, 0)))

	def __readPacket(self):
		"""
		Receive a packet from fingerprint sensor.

		Return a tuple that contain the following information:
		0: integer(1 byte) The packet type.
		1: integer(n bytes) The packet payload.

		@return tuple
		"""

		receivedPacketData = []
		i = 0

		while ( True ):

			## Read one byte
			receivedFragment = self.__serial.read()

			if ( len(receivedFragment) != 0 ):
				receivedFragment = stringToByte(receivedFragment)
				## print 'Received packet fragment = ' + hex(receivedFragment)

			## Insert byte if packet seems valid
			receivedPacketData.insert(i, receivedFragment)
			i += 1

			## Packet could be complete (the minimal packet size is 12 bytes)
			if ( i >= 12 ):

				## Check the packet header
				if ( receivedPacketData[0] != shiftRight(FINGERPRINT_STARTCODE, 8) or receivedPacketData[1] != shiftRight(FINGERPRINT_STARTCODE, 0) ):
					raise Exception('The received packet do not begin with a valid header!')

				## Calculate packet payload length (combine the 2 length bytes)
				packetPayloadLength = shiftLeft(receivedPacketData[7], 8)
				packetPayloadLength = packetPayloadLength | shiftLeft(receivedPacketData[8], 0)

				## Check if the packet is still fully received
				## Condition: index counter < packet payload length + packet frame
				if ( i < packetPayloadLength + 9 ):
					continue

				## At this point the packet should be fully received

				packetType = receivedPacketData[6]

				## Calculate checksum:
				## checksum = packet type (1 byte) + packet length (2 bytes) + packet payload (n bytes)
				packetChecksum = packetType + receivedPacketData[7] + receivedPacketData[8]

				packetPayload = []

				## Collect package payload (ignore the last 2 checksum bytes)
				for j in range(9, 9 + packetPayloadLength - 2):
					packetPayload.append(receivedPacketData[j])
					packetChecksum += receivedPacketData[j]

				## Calculate full checksum of the 2 separate checksum bytes
				receivedChecksum = shiftLeft(receivedPacketData[i - 2], 8)
				receivedChecksum = receivedChecksum | shiftLeft(receivedPacketData[i - 1], 0)

				if ( receivedChecksum != packetChecksum ):
					raise Exception('The received packet is corrupted (the checksum is wrong)!')

				return (packetType, packetPayload)

	def verify_password(self):
		"""
		Verifie password of the fingerprint sensor.

		@return boolean
		"""

		packetPayload = (
			FINGERPRINT_VERIFYPASSWORD,
			shiftRight(self.__password, 24),
			shiftRight(self.__password, 16),
			shiftRight(self.__password, 8),
			shiftRight(self.__password, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Sensor password is correct
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: Sensor password is wrong
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_WRONGPASSWORD ):
			return False

		else:
			raise Exception('Unknown error')

	def set_password(self, newPassword):
		"""
		Set the password of the sensor.

		@param integer(4 bytes) newPassword
		@return boolean
		"""

		## Validate the password (maximum 4 bytes)
		if ( newPassword < 0x00000000 or newPassword > 0xFFFFFFFF ):
			raise ValueError('The given password is invalid!')

		packetPayload = (
			FINGERPRINT_SETPASSWORD,
			shiftRight(newPassword, 24),
			shiftRight(newPassword, 16),
			shiftRight(newPassword, 8),
			shiftRight(newPassword, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Password set was successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		else:
			raise Exception('Unknown error')

	def set_address(self, newAddress):
		"""
		Set the module address of the sensor.

		@param integer(4 bytes) newAddress
		@return boolean
		"""

		## Validate the address (maximum 4 bytes)
		if ( newAddress < 0x00000000 or newAddress > 0xFFFFFFFF ):
			raise ValueError('The given address is invalid!')

		packetPayload = (
			FINGERPRINT_SETADDRESS,
			shiftRight(newAddress, 24),
			shiftRight(newAddress, 16),
			shiftRight(newAddress, 8),
			shiftRight(newAddress, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Address set was successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		else:
			raise Exception('Unknown error')

	def set_system_parameter(self, parameterNumber, parameterValue):
		"""
		Sets a system parameter of the sensor.

		@param integer(1 byte) parameterNumber
		@param integer(1 byte) parameterValue
		@return boolean
		"""

		## Validate the baudrate parameter
		if ( parameterNumber == 4 ):

			if ( parameterValue < 1 or parameterValue > 12 ):
				raise ValueError('The given baudrate parameter is invalid!')

		## Validate the security level parameter
		elif ( parameterNumber == 5 ):

			if ( parameterValue < 1 or parameterValue > 5 ):
				raise ValueError('The given security level parameter is invalid!')

		## Validate the package length parameter
		elif ( parameterNumber == 6 ):

			if ( parameterValue < 0 or parameterValue > 3 ):
				raise ValueError('The given package length parameter is invalid!')

		## The parameter number is not valid
		else:
			raise ValueError('The given parameter number is invalid!')

		packetPayload = (
			FINGERPRINT_SETSYSTEMPARAMETER,
			parameterNumber,
			parameterValue,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Parameter set was successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDREGISTER ):
			raise Exception('Invalid register number')

		else:
			raise Exception('Unknown error')

	def get_system_parameters(self):
		"""
		Get all available system information of the sensor.

		Return a tuple that contain the following information:
		0: integer(2 bytes) The status register.
		1: integer(2 bytes) The system id.
		2: integer(2 bytes) The storage capacity.
		3: integer(2 bytes) The security level.
		4: integer(4 bytes) The sensor address.
		5: integer(2 bytes) The packet length.
		6: integer(2 bytes) The baudrate.

		@return tuple
		"""

		packetPayload = (
			FINGERPRINT_GETSYSTEMPARAMETERS,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Read successfully
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

			statusRegister	 = shiftLeft(receivedPacketPayload[1], 8) | shiftLeft(receivedPacketPayload[2], 0)
			systemID		   = shiftLeft(receivedPacketPayload[3], 8) | shiftLeft(receivedPacketPayload[4], 0)
			storageCapacity	= shiftLeft(receivedPacketPayload[5], 8) | shiftLeft(receivedPacketPayload[6], 0)
			securityLevel	  = shiftLeft(receivedPacketPayload[7], 8) | shiftLeft(receivedPacketPayload[8], 0)
			deviceAddress	  = ((receivedPacketPayload[9] << 8 | receivedPacketPayload[10]) << 8 | receivedPacketPayload[11]) << 8 | receivedPacketPayload[12] ## TODO
			packetLength	   = shiftLeft(receivedPacketPayload[13], 8) | shiftLeft(receivedPacketPayload[14], 0)
			baudRate		   = shiftLeft(receivedPacketPayload[15], 8) | shiftLeft(receivedPacketPayload[16], 0)

			return (statusRegister, systemID, storageCapacity, securityLevel, deviceAddress, packetLength, baudRate)

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		else:
			raise Exception('Unknown error')

	def get_template_index(self, page):
		"""
		Get a list of the template positions with usage indicator.

		@param integer(1 byte) page
		@return list
		"""

		if ( page < 0 or page > 3 ):
			raise ValueError('The given index page is invalid!')

		packetPayload = (
			FINGERPRINT_TEMPLATEINDEX,
			page,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Read index table successfully
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

			templateIndex = []

			## Contain the table page bytes (skip the first status byte)
			pageElements = receivedPacketPayload[1:]

			for pageElement in pageElements:
				## Test every bit (bit = template position is used indicator) of a table page element
				for p in range(0, 7 + 1):
					positionIsUsed = (utilities.bitAtPosition(pageElement, p) == 1)
					templateIndex.append(positionIsUsed)

			return templateIndex

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		else:
			raise Exception('Unknown error')

	def get_template_count(self):
		"""
		Get the number of stored templates.

		@return integer(2 bytes)
		"""

		packetPayload = (
			FINGERPRINT_TEMPLATECOUNT,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Read successfully
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			templateCount = shiftLeft(receivedPacketPayload[1], 8)
			templateCount = templateCount | shiftLeft(receivedPacketPayload[2], 0)
			return templateCount

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		else:
			raise Exception('Unknown error')

	def read_image(self):
		"""
		Read the image of a finger and stores it in ImageBuffer.

		@return boolean
		"""

		packetPayload = (
			FINGERPRINT_READIMAGE,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Image read successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: No finger found
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_NOFINGER ):
			return False

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_READIMAGE ):
			raise Exception('Could not read image')

		else:
			raise Exception('Unknown error')

	## TODO:
	## Implementation of uploadImage()

	def download_image(self, imageDestination):
		"""
		Download the image of a finger to host computer.

		@param string imageDestination
		@return void
		"""

		destinationDirectory = os.path.dirname(imageDestination)

		if ( os.access(destinationDirectory, os.W_OK) == False ):
			raise ValueError('The given destination directory "' + destinationDirectory + '" is not writable!')

		packetPayload = (
			FINGERPRINT_DOWNLOADIMAGE,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

		## Get first reply packet
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: The sensor will sent follow-up packets
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			pass

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_DOWNLOADIMAGE ):
			raise Exception('Could not download image')

		else:
			raise Exception('Unknown error')

		## Initialize image library
		resultImage = Image.new('L', (256, 288), 'white')
		pixels = resultImage.load()

		## Y coordinate of current pixel
		line = 0

		## Get follow-up data packets until the last data packet is received
		while ( receivedPacketType != FINGERPRINT_ENDDATAPACKET ):

			receivedPacket = self.__readPacket()

			receivedPacketType = receivedPacket[0]
			receivedPacketPayload = receivedPacket[1]

			if ( receivedPacketType != FINGERPRINT_DATAPACKET and receivedPacketType != FINGERPRINT_ENDDATAPACKET ):
				raise Exception('The received packet is no data packet!')

			## X coordinate of current pixel
			x = 0

			for i in range(0, len(receivedPacketPayload)):

				## Thanks to Danylo Esterman <soundcracker@gmail.com> for the "multiple with 17" improvement:

				## Draw left 4 Bits one byte of package
				pixels[x, line] = (receivedPacketPayload[i] >> 4) * 17
				x = x + 1

				## Draw right 4 Bits one byte of package
				pixels[x, line] = (receivedPacketPayload[i] & 0b00001111) * 17
				x = x + 1

			line = line + 1

		resultImage.save(imageDestination)

	def convert_image(self, charBufferNumber = 0x01):
		"""
		Convert the image in ImageBuffer to finger characteristics and store in CharBuffer1 or CharBuffer2.

		@param integer(1 byte) charBufferNumber
		@return boolean
		"""

		if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
			raise ValueError('The given charbuffer number is invalid!')

		packetPayload = (
			FINGERPRINT_CONVERTIMAGE,
			charBufferNumber,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Image converted
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_MESSYIMAGE ):
			raise Exception('The image is too messy')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_FEWFEATUREPOINTS ):
			raise Exception('The image contains too few feature points')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDIMAGE ):
			raise Exception('The image is invalid')

		else:
			raise Exception('Unknown error')

	def create_template(self):
		"""
		Combine the characteristics which are stored in CharBuffer1 and CharBuffer2 to a template.
		The created template will be stored again in CharBuffer1 and CharBuffer2 as the same.

		@return boolean
		"""

		packetPayload = (
			FINGERPRINT_CREATETEMPLATE,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Template created successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: The characteristics not matching
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH ):
			return False

		else:
			raise Exception('Unknown error')

	def store_template(self, positionNumber, charBufferNumber = 0x01):
		"""
		Save a template from the specified CharBuffer to the given position number.

		@param integer(2 bytes) positionNumber
		@param integer(1 byte) charBufferNumber
		@return boolean
		"""

		if ( positionNumber < 0x0000 or positionNumber > 0x00A3 ):
			raise ValueError('The given position number is invalid!')

		if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
			raise ValueError('The given charbuffer number is invalid!')

		packetPayload = (
			FINGERPRINT_STORETEMPLATE,
			charBufferNumber,
			shiftRight(positionNumber, 8),
			shiftRight(positionNumber, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Template stored successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDPOSITION ):
			raise Exception('Could not store template in that position')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_FLASH ):
			raise Exception('Error writing to flash')

		else:
			raise Exception('Unknown error')

	def search_template(self):
		"""
		Search the finger characteristiccs in CharBuffer in database.

		Return a tuple that contain the following information:
		0: integer(2 bytes) The position number of found template.
		1: integer(2 bytes) The accuracy score of found template.

		@return tuple
		"""

		## CharBuffer1 and CharBuffer2 are the same in this case
		charBufferNumber = 0x01

		## Begin search at page 0x0000 for 0x00A3 (means 163) templates
		positionStart = 0x0000
		templatesCount = 0x00A3

		packetPayload = (
			FINGERPRINT_SEARCHTEMPLATE,
			charBufferNumber,
			shiftRight(positionStart, 8),
			shiftRight(positionStart, 0),
			shiftRight(templatesCount, 8),
			shiftRight(templatesCount, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Found template
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

			positionNumber = shiftLeft(receivedPacketPayload[1], 8)
			positionNumber = positionNumber | shiftLeft(receivedPacketPayload[2], 0)

			accuracyScore = shiftLeft(receivedPacketPayload[3], 8)
			accuracyScore = accuracyScore | shiftLeft(receivedPacketPayload[4], 0)

			return (positionNumber, accuracyScore)

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: Did not found a matching template
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_NOTEMPLATEFOUND ):
			return (-1, -1)

		else:
			raise Exception('Unknown error')

	def load_template(self, positionNumber, charBufferNumber = 0x01):
		"""
		Load an existing template specified by position number to specified CharBuffer.

		@param integer(2 bytes) positionNumber
		@param integer(1 byte) charBufferNumber
		@return boolean
		"""

		if ( positionNumber < 0x0000 or positionNumber > 0x00A3 ):
			raise ValueError('The given position number is invalid!')

		if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
			raise ValueError('The given charbuffer number is invalid!')

		packetPayload = (
			FINGERPRINT_LOADTEMPLATE,
			charBufferNumber,
			shiftRight(positionNumber, 8),
			shiftRight(positionNumber, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Template loaded successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_LOADTEMPLATE ):
			raise Exception('The template could not be read')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDPOSITION ):
			raise Exception('Could not load template from that position')

		else:
			raise Exception('Unknown error')

	def delete_template(self, positionNumber):
		"""
		Delete one template from fingerprint database.

		@param integer(2 bytes) positionNumber
		@return boolean
		"""

		if ( positionNumber < 0x0000 or positionNumber > 0x00A3 ):
			raise ValueError('The given position number is invalid!')

		## Delete only one template
		count = 0x0001

		packetPayload = (
			FINGERPRINT_DELETETEMPLATE,
			shiftRight(positionNumber, 8),
			shiftRight(positionNumber, 0),
			shiftRight(count, 8),
			shiftRight(count, 0),
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Template deleted successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: Could not delete template
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_DELETETEMPLATE ):
			return False

		else:
			raise Exception('Unknown error')

	def clear_database(self):
		"""
		Clear the complete template database.

		@return boolean
		"""

		packetPayload = (
			FINGERPRINT_CLEARDATABASE,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Database cleared successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			return True

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: Could not clear database
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_CLEARDATABASE ):
			return False

		else:
			raise Exception('Unknown error')

	def compare_characteristics(self):
		"""
		Compare the finger characteristics of CharBuffer1 with CharBuffer2 and return the accuracy score.

		@return integer(2 bytes)
		"""

		packetPayload = (
			FINGERPRINT_COMPARECHARACTERISTICS,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: Comparation successful
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			accuracyScore = shiftLeft(receivedPacketPayload[1], 8)
			accuracyScore = accuracyScore | shiftLeft(receivedPacketPayload[2], 0)
			return accuracyScore

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		## DEBUG: The characteristics do not matching
		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_NOTMATCHING ):
			return 0

		else:
			raise Exception('Unknown error')

	def upload_characteristics(self, charBufferNumber = 0x01, characteristicsData = [0]):
		"""
		Upload finger characteristics to CharBuffer1 or CharBuffer2.

		@author: David Gilson <davgilson@live.fr>

		@param integer(1 byte) charBufferNumber
		@param integer(list) characteristicsData

		@return boolean
		Return true if everything is right.
		"""

		if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
			raise ValueError('The given charbuffer number is invalid!')

		if ( characteristicsData == [0] ):
			raise ValueError('The characteristics data is required!')

		maxPacketSize = self.getMaxPacketSize()

		## Upload command

		packetPayload = (
			FINGERPRINT_UPLOADCHARACTERISTICS,
			charBufferNumber
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

		## Get first reply packet
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: The sensor will sent follow-up packets
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			pass

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_PACKETRESPONSEFAIL ):
			raise Exception('Could not upload characteristics')

		else:
			raise Exception('Unknown error')

		## Upload data packets
		packetNbr = len(characteristicsData) / maxPacketSize

		if ( packetNbr <= 1 ):
			self.__writePacket(FINGERPRINT_ENDDATAPACKET, characteristicsData)
		else:
			i = 1
			while ( i < packetNbr ):
				lfrom = (i-1) * maxPacketSize
				lto = lfrom + maxPacketSize
				self.__writePacket(FINGERPRINT_DATAPACKET, characteristicsData[lfrom:lto])
				i += 1

			lfrom = (i-1) * maxPacketSize
			lto = lfrom + maxPacketSize
			self.__writePacket(FINGERPRINT_ENDDATAPACKET, characteristicsData[lfrom:lto])

		## Verify uploaded characteristics
		characterics = self.downloadCharacteristics(charBufferNumber)
		return (characterics == characteristicsData)

	def get_max_packet_size(self):
		"""
		Get the maximum allowed size of packet by sensor.

		@author: David Gilson <davgilson@live.fr>

		@return int
		Return the max size. Default 32 bytes.
		"""

		packetMaxSizeType = self.getSystemParameters()[5]

		if (packetMaxSizeType == 1):
			return 64
		elif (packetMaxSizeType == 2):
			return 128
		elif (packetMaxSizeType == 3):
			return 256
		else:
			return 32

	def download_characteristics(self, charBufferNumber = 0x01):
		"""
		Download the finger characteristics of CharBuffer1 or CharBuffer2.

		@param integer(1 byte) charBufferNumber

		@return list
		Return a list that contains 512 integer(1 byte) elements of the characteristic.
		"""

		if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
			raise ValueError('The given charbuffer number is invalid!')

		packetPayload = (
			FINGERPRINT_DOWNLOADCHARACTERISTICS,
			charBufferNumber,
		)

		self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

		## Get first reply packet
		receivedPacket = self.__readPacket()

		receivedPacketType = receivedPacket[0]
		receivedPacketPayload = receivedPacket[1]

		if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
			raise Exception('The received packet is no ack packet!')

		## DEBUG: The sensor will sent follow-up packets
		if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
			pass

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
			raise Exception('Communication error')

		elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_DOWNLOADCHARACTERISTICS ):
			raise Exception('Could not download characteristics')

		else:
			raise Exception('Unknown error')

		completePayload = []

		## Get follow-up data packets until the last data packet is received
		while ( receivedPacketType != FINGERPRINT_ENDDATAPACKET ):

			receivedPacket = self.__readPacket()

			receivedPacketType = receivedPacket[0]
			receivedPacketPayload = receivedPacket[1]

			if ( receivedPacketType != FINGERPRINT_DATAPACKET and receivedPacketType != FINGERPRINT_ENDDATAPACKET ):
				raise Exception('The received packet is no data packet!')

			for i in range(0, len(receivedPacketPayload)):
				completePayload.append(receivedPacketPayload[i])

		return completePayload

	def enroll_user(self, capture_count=4):
		"""
		Take a picture, get characterics and repeat n times
		@param capture_count : How many times do we capture the fingerprint

		@return array [capture_index][characterics]
		"""
		user_characteristics = []
		captured = 0

		#Check connection
		if self.verify_password() == True:
			while(captured < capture_count):
				## Waiting for finger
				print("Waiting for finger")
				while (self.read_image() == False):
					time.sleep(2)

				## Converts read image to characteristics and stores it in charbuffer 2
				self.convert_image(0x02)

				## Download characteristics
				characteristics = self.download_characteristics(0x02)

				## Append to user characterics
				user_characteristics.append((captured, characteristics))
				captured += 1

		return user_characteristics

	def match_fingerprint_characteristics(self, characteristics = [0]):
		"""
		Take a picture of user finger and send matching characteristics
		@return boolean : True when characteristics match
		"""
		## Check connection
		if self.verify_password() == True:
			## Upload characteristics
			if self.upload_characteristics(charBufferNumber = 0x01, characteristicsData = characteristics) == True:
				## Waiting for finger
				print("Waiting for finger")
				while (self.read_image() == False):
					time.sleep(2)

				## Converts read image to characteristics and stores it in charbuffer 2
				self.convert_image(0x02)

				score = 0

				try:
					score = self.compare_characteristics()
				except:
					pass

				return (score >= FINGERPRINT_ACCURACY_MINI_SCORE)

	def activate_fingerprint_control(self):
		"""
			Try to read a fingerprint and extract characteristics
			@return characteristics or 0x00 if nothing was read
		"""
		if (self.read_image() == True):
			## Converts read image to characteristics and stores it in charbuffer 2
			self.convert_image(0x02)

			## Download characteristics
			characteristics = self.download_characteristics(0x02)

			return characteristics
		else:
			return None


if __name__ == "__main__":
	with ZFM20_Device() as device:
		user_chars = device.enroll_user()

		if(len(user_chars) > 0):
			print("Enrolled")
			print(user_chars)
		else:
			print("Error")
