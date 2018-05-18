#!/usr/bin/env python
# Relative import
import sys
sys.path.append('..')
from lib.devices.protocols.wiegand import WiegandReader
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

  with WiegandReader(GPIO, 14, 15, callback) as w:
      while True:
          time.sleep(300)
      w.cancel()
