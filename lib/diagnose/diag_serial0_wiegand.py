import serial;

try:
    with serial.Serial('/dev/serial0', 115200, timeout=1) as ser:
        while True:
        	s = ser.read(100)
        	print(str(s))
except serial.serialutil.SerialException:
    print("Cannot open port")
