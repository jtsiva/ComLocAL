#!/usr/bin/python
"""
Basic usage of module for use with debugger

"""

from comlocal.core import Com
import json
import pdb
pdb.set_trace()

com = Com.Com()
com.write(json.loads('{"type": "msg", "payload": "Hello world!"}'))
print com.read()