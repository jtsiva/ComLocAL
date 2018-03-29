#!/usr/bin/python

from comlocal.interface import ComIFace
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import time
import argparse


from twisted.python import log

class myThing(object):
	def __init__(self):
		self.read = 0
		self.cmdRes = 0
		self.writes = 0
		self.readyToSend = False
		self.max = 0
		self.start = None

	def reader(self, msg):
		if 0 == self.read:
			self.start = time.time()

		self.read += 1
		if self.read == self.max:
			print 'received %d in %f seconds' % (self.max, time.time() - self.start)

	def writeRes(self):
		#log.msg(msg)
		last = time.time()
		self.writes += 1

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-c", "--count", required = True, help="set the number messages that sender should send")
	parser.add_argument ("-s", "--sender", action="store_true", default=False, help="set whether this device will send")
	parser.add_argument ("-d", "--dest", required = True, help="set the destination for the message")
	parser.add_argument ("-p", "--period", required = False, help="time between writes in seconds (float)")


	args =  parser.parse_args()

	thing = myThing()

	myCom = ComIFace.ComIFace('TEST',10789)
	myCom.readCB = thing.reader
	
	count = int(args.count)
	sender = args.sender
	dest = int(args.dest)
	period = float(args.period) if args.period is not None else .001

	thing.max = count

	if sender:
		def failed(reason):
			print reason

		def writeThing():
			# print 'hello'
			# log.msg('hello')
			if thing.writes == count:
				d = myCom.stop()
				d.addCallbacks(lambda res: reactor.stop(), failed)
			else:
				d = myCom.write('hello', dest)
				d.addCallback(lambda res: thing.writeRes())
				d.addCallbacks(lambda res: reactor.callLater(period, writeThing),lambda res: reactor.callLater(period, writeThing))

			return d

		d = myCom.start()
		d.addCallbacks(lambda res: reactor.callLater(period, writeThing), failed)
	else:
		myCom.start()

	reactor.run()
	print thing.writes
#

if __name__ == "__main__":
	main()