#!/usr/bin/python
from __future__ import print_function
from comlocal.interface import ComIFace

from twisted.internet import reactor
from twisted.protocols import basic
from twisted.internet import stdio

import time
import argparse
import json


from twisted.python import log

class IOHandler(basic.LineReceiver):
	def __init__(self):
		self._buffer = ""
		self.frame_size = 512 #FRAME SIZE HERE
		self.writeHandler = None
		self.bytesReceived = 0
		self.bytesSent = 0
		self.bytesSent
		self.last = 0
		self.reads = 0
		self.writes = 0
		self.start = None
		self.lastTime = None
		self.pendingFlush = None

	def connectionMade(self):
		pass

	def connectionLost(self, reason):
		reactor.stop()

	def rawDataReceived(self, data):

		#we have new data, so wait to flush the buffer
		if self.pendingFlush is not None:
			self.pendingFlush.cancel()
			self.pendingFlush = None

		self._buffer = self._buffer + data
		frame_size = self.frame_size
		while len(self._buffer) >= frame_size:
			self.frameReceived(self._buffer[0:frame_size])
			self._buffer = self._buffer[frame_size:]

		#if we have leftover bytes, wait twice as long as the average time per packet
		#then send a partial packet
		if 0 < len(self._buffer):
			waitTime = (2 * (time.time() - self.start) / self.writes) if self.writes else .0001
			self.pendingFlush = reactor.callLater(waitTime, self.flushBuffer)

	def flushBuffer(self):
		self.frameReceived(self._buffer)
		self.buffer = ""

	def frameReceived(self,data):
		now = time.time()
		if 0 == self.writes:
			self.start = now

		self.lastTime = now

		self.bytesSent += len(data)
		self.writes += 1
		if self.writeHandler is not None:
			self.writeHandler(data)
		else:
			self.readHandler(data) #bounce back

	def readHandler(self, data):
		now = time.time()
		self.bytesReceived += len(data['msg'])
		if 0 == self.reads:
			self.start = now

		self.reads += 1
		self.lastTime = now
		print(data['msg'])

	def printStats(self):
		if self.bytesSent:
			print('Sent %d bytes in %f seconds' % (self.bytesSent, self.lastTime - self.start))

		if self.bytesReceived:
			print('Received %d bytes in %f seconds' % (self.bytesReceived, self.lastTime - self.start))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-l", "--listener", action="store_true", default=False, help="set whether this device will listen")
	parser.add_argument ("-n", "--name", required = True, help="set the name of application (for both sending and receiving)")
	parser.add_argument ("-t", "--timeout", required = False, default="0", help="time to wait before connection is closed")
	parser.add_argument ("-m", "--message", required = False, default="", help="message to send (if - is used then stdin is assumed)")
	parser.add_argument ("-s", "--stats", action="store_true", default=False, help="set whether statistics will be printed once the program finishes")
	parser.add_argument ("-d", "--dest", required = False, help="set the destination for the message")

	args =  parser.parse_args()

	ioThing = IOHandler()

	myCom = ComIFace.ComIFace(args.name)
	
	listener = args.listener
	timeout = float(args.timeout)
	message = args.message
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
			exit()

		# if not ("-" == message):
		# 	d = myCom.start()
		# 	d.addCallback(lambda _: writeData(args.message))
		# 	d.addCallback(lambda _: myCom.stop())
		# 	d.addCallback(lambda _: reactor.stop())
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