#!/usr/bin/python
import sys
path='/app/omni'
if path not in sys.path:
    sys.path.append(path)
from server import app as application
