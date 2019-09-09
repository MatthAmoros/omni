#!/usr/bin/env python
import signal, os
from lib.common import PrintColor

try:
	import RPi.GPIO as GPIO
	is_running_on_pi = True
except RuntimeError:
	print(PrintColor.WARNING + "Starting without GPIO")
	is_running_on_pi = False
	pass
"""
bits=26 value=12442091
bits=26 value=45883139
bits=26 value=45883139
bits=26 value=45883139
bits=26 value=45883139
bits=26 value=12442091
# Set the signal handler
#signal.signal(signal.SIGALRM, self._on_timedout)
#signal.setitimer(signal.ITIMER_REAL, 0.1) #Alarm in 100ms

def _on_timedout(self, signum, frame):
    signal.setitimer(signal.ITIMER_REAL, 0)          # Disable the alarm
    self.is_reading = False
    self.callback(self.bits, self.num)

"""

class WiegandReader:
    def __init__(self, gpio, board_gpio_data0, board_gpio_data1, callback, bit_size=26):
        """
            gpio is meant to be RPI.GPIO module
            board_gpio_data0 : DATA0 wire
            board_gpio_data1 : DATA1 wire
        """

        self.gpio = gpio
        self.gpio_0 = board_gpio_data0
        self.gpio_1 = board_gpio_data1

        self.callback = callback

        self.bits = 0
        self.num = 0

        self.is_reading = False
        self.is_timedout = False
        self.bit_size = bit_size
        self.string_code = ""

        """
        Avoid warning about ports already in use
        """
        self.gpio.setwarnings(False)

        """
        Set wiring index mode
        """
        self.gpio.setmode(GPIO.BCM)

        """
        Setting GPIO as input
        """
        self.gpio.setup(self.gpio_0, GPIO.IN)
        self.gpio.setup(self.gpio_1, GPIO.IN)

        """
        Using pull up to set defaut state to True
        According to Wiegand specifications, where DATA0 and DATA1 are set to 1, no data is transmitted
        """
        self.gpio.setup(self.gpio_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.gpio.setup(self.gpio_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def __enter__(self):
        """
        When DATA0 = 0 or DATA1 = 0 data is transmitted
        """
        self.gpio.add_event_detect(self.gpio_0, GPIO.FALLING, callback=self._on_data_received)
        self.gpio.add_event_detect(self.gpio_1, GPIO.FALLING, callback=self._on_data_received)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cancel()

    def _on_data_received(self, gpio):
        if self.bits > 0:
            self.num = self.num << 1

        if gpio == self.gpio_1:
            self.num = self.num | 1
            self.string_code = self.string_code + "1"
        else:
            self.string_code = self.string_code + "0"

        self.bits += 1

        if self.bits >= self.bit_size:
            self.callback(self.bits, self.num)
            print(self.string_code)
            self.string_code = ""
            """ Reset counters """
            self.bits = 0
            self.num = 0

    def cancel(self):

        """
        Cancel the Wiegand decoder.
        """
        self.gpio.setmode(GPIO.BCM)
        self.gpio.remove_event_detect(self.gpio_0)
        self.gpio.remove_event_detect(self.gpio_1)
        self.gpio.cleanup()
