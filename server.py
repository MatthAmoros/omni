#!/usr/bin/env python
from flask import Flask
from flask import request

app = Flask(__name__)

#Flask definitions
@app.route("/isAlive")
def index():
    return "200"
    
@app.route("/accessRule/<zone>/<credential>", methods=['GET'])
def validateCredential():
	if zone == '1':
		return "200"
	else:
		return "401"

print "Start web server..."
app.run(host='0.0.0.0')
