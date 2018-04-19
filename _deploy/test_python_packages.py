try:
	import flask
except ImportError, e:
	print "Module Flask doesn't exist"

try:
	import RPi.GPIO
except ImportError, e:
	print "Module RPi.GPIO doesn't exist"
except RuntimeError:
	print "Not running on a Raspberry Pi board"
	
try:	
	import pyodbc 
except ImportError, e:
	print "Module pyODBC doesn't exist"
