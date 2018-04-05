#!/usr/bin/python

from comlocal.interface import ComIFace
from comlocal.applications import IOHandler

from twisted.internet import stdio
from twisted.internet import reactor

import argparse

from twisted.python import log



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-l", "--listener", action="store_true", default=False, help="set whether this device will listen")
	parser.add_argument ("-n", "--name", required = True, help="set the name of application (for both sending and receiving)")
	parser.add_argument ("-t", "--timeout", required = False, default="0", help="time to wait before connection is closed")
	parser.add_argument ("-s", "--stats", action="store_true", default=False, help="set whether statistics will be printed once the program finishes")
	parser.add_argument ("-d", "--dest", required = False, help="set the destination for the message")

	args =  parser.parse_args()

	ioThing = IOHandler.IOHandler()

	myCom = ComIFace.ComIFace(args.name)
	
	listener = args.listener
	timeout = float(args.timeout)
	dest = int(args.dest) if args.dest is not None else None

	def failed(reason):
		print(reason)

	def writeData(data):
		d = myCom.write(data, dest)
		return d

	ioThing.writeHandler = writeData
	myCom.readCB = ioThing.readHandler
	ioThing.setRawMode()
	stdio.StandardIO(ioThing)

	if not listener:
		if dest is None:
			print ("No destination specified!")
			exit()
		myCom.start()
	else:
		def check():
			if ioThing.last == ioThing.read:
				d = myCom.stop()
				d.addCallbacks(lambda _: reactor.stop(), failed)
			else:
				ioThing.last = ioThing.reads
				reactor.callLater(timeout, check)

		d = myCom.start()
		if timeout != 0:
			d.addCallbacks(lambda _: reactor.callLater(timeout, check), failed)

	reactor.run()

	if args.stats:
		ioThing.printStats()
#

if __name__ == "__main__":
	main()