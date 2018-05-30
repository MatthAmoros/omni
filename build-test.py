""" This file is used by Travis to test code """
from server import *
from client import *
from lib.sourceFactory import *
from lib.common import *
from lib.devices.deviceBase import *

import os
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        print("Setting up tests")
    def tearDown(self):
        print("Tearing down tests")

if __name__ == '__main__':
    unittest.main()
