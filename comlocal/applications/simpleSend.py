#!/usr/bin/python

from comlocal.connection import ConnectionLayer
from twisted.python import log

from comlocal.applications import IOHandler

from twisted.internet import stdio
from twisted.internet import reactor
from twisted.internet.defer import Deferred, maybeDeferred

import json
import argparse

from twisted.python import log

class container(object):
	def __init__(self, configFile, readHandler):
		self._commonData = {}
		self._initCommonData(configFile)
		self._CL = ConnectionLayer.ConnectionLayer(self._commonData)
		self._CL.setReadCB(readHandler)
		self.radioBcast = {}

		for radioName in self._commonData['startRadios']:
			self._setupRadio(radioName)

	def _initCommonData(self, configFile):
		"""
		Init the common data by, say, reading from a file
		"""
		if configFile is not None:
			with open(configFile, 'r') as f:
				self._commonData = json.loads(f.read())
		else:
			self._commonData['id'] = random.randrange(255)
			self._commonData['location'] = [0,0,0]
			self._commonData['startRadios'] = ['WiFi', 'Loopback']
			self._commonData['activeRadios'] = []
			self._commonData['blacklist'] = []

		self._commonData['logging'] = {'inUse': False} if not log else {'inUse': True}
	#

	def _setupRadio (self, radioName):
		self._CL.addRadio(radioName)
		bcastAddr = self._CL.write({'cmd':'get_radio_props', 'name':radioName})['result']['bcastAddr']
		self.radioBcast[radioName] = bcastAddr


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument ("-f", "--config", required = False, help="configuration file")
	parser.add_argument ("-n", "--name", required = True, help="set the name of application (for both sending and receiving)")
	parser.add_argument ("-t", "--timeout", required = False, default="0", help="time to wait before connection is closed")
	parser.add_argument ("-s", "--stats", action="store_true", default=False, help="set whether statistics will be printed once the program finishes")
	parser.add_argument ("-d", "--dest", required = False, help="set the destination for the message")
	parser.add_argument ("-c", "--chunksize", required = False, default="512", help="set the max size of the chunks (in bytes) into which the input is broken")

	global msgID
	msgID = 0
	args =  parser.parse_args()

	ioThing = IOHandler.IOHandler(int(args.chunksize))
	
	timeout = float(args.timeout)
	dest = int(args.dest) if args.dest is not None else None

	myContainer = container(args.config, ioThing.readHandler)

	message = {'msgId':msgID,'src':myContainer._commonData['id'],'dest':dest,'app':args.name}
	radioList = []
	for radio in myContainer._commonData['startRadios']:
		radioList.append((radio, myContainer.radioBcast[radio]))

	def failed(reason):
		print(reason)

	def writeData(data):
		global msgID
		message['msgId'] = msgID
		message['msg'] = data

		

		message['radios'] = radioList
		
		try:
			tmp = message.pop('result')
		except KeyError:
			pass
		d = maybeDeferred(myContainer._CL.write, message)
		msgID += 1
		return d


	def stop(reason):
		if ioThing.empty:
			reactor.stop()
		else:
			reactor.callLater(.001, stop, reason)

	ioThing.writeHandler = writeData
	ioThing.stopHandler = stop
	ioThing.setRawMode()
	

	if dest is None:
		print ("No destination specified!")
		exit()
	stdio.StandardIO(ioThing)
	
	reactor.run()

	if args.stats:
		ioThing.printStats()
#

if __name__ == "__main__":
	main()