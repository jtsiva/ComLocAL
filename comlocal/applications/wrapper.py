#!/usr/bin/python

from comlocal.applications import IOHandler

from twisted.internet import stdio
from twisted.internet import reactor
from twisted.internet.defer import Deferred

import json
import argparse

from twisted.python import log



def main():
	parser = argparse.ArgumentParser()
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

	message = {'msgId':msgID,'src':9,'dest':dest,'app':args.name}

	def failed(reason):
		print(reason)

	def writeData(data):
		global msgID
		message['msgId'] = msgID
		message['msg'] = data
		print(json.dumps(message, separators=(',', ':')))
		msgID += 1
		return Deferred()


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