#!/usr/bin/env python

import access-ctrl-hid.devices.protocols.wiegand as wiegand
import RPi.GPIO as GPIO
"""
bits=26 value=12442091
bits=26 value=45883139
bits=26 value=45883139
bits=26 value=45883139
bits=26 value=45883139
bits=26 value=12442091

"""

if __name__ == "__main__":
   import time


   def callback(bits, value):
      print("bits={} value={}".format(bits, value))

   pi = GPIO

   w = wiegand.WiegandReader(pi, 14, 15, callback)

   while True:
       time.sleep(300)

   w.cancel()
