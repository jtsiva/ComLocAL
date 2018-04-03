#!/usr/bin/python

from comlocal.interface import ComIFace
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import time
import argparse
import json


from twisted.python import log

class myThing(object):
	def __init__(self):
		self.read = 0
		self.cmdRes = 0
		self.writes = 0
		self.readyToSend = False
		self.max = 0
		self.start = None
		self.last = 0
		self.lastTime = None
		self.msgSize = 0
		self.totalSize = 0

	def reader(self, msg):
		now = time.time()
		if 0 == self.read:
			self.totalSize = len(json.dumps(msg, separators=(',', ':')))
			self.msgSize = len(msg['msg'])
			self.start = now

		self.read += 1
		self.lastTime = now
		

	def printRes(self):
		if self.lastTime and self.start:
			print 'received %d messages in %f seconds' % (self.read, self.lastTime - self.start)
			print 'total throughput: %f bytes per second' % ((self.totalSize * self.read) / (self.lastTime - self.start))
			print 'payload throughput: %f bytes per second' % ((self.msgSize * self.read) / (self.lastTime - self.start))
			with open('run.txt', 'w') as f:
				f.write("%d,%f,%f" % (self.read, self.lastTime - self.start, (self.totalSize * self.read) / (self.lastTime - self.start)))

		else:
			print 'nothing received'

	def writeRes(self):
		now = time.time()
		if 0 == self.writes:
			self.start = now
		self.lastTime = now
		self.writes += 1

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-c", "--count", required = False, help="set the number messages that sender should send")
	parser.add_argument ("-s", "--sender", action="store_true", default=False, help="set whether this device will send")
	parser.add_argument ("-d", "--dest", required = False, help="set the destination for the message")
	parser.add_argument ("-p", "--period", required = False, help="time between writes in seconds (float)")
	parser.add_argument ("-m", "--message", required = False, help="message to send")


	args =  parser.parse_args()

	thing = myThing()

	myCom = ComIFace.ComIFace('TEST',10789)
	myCom.readCB = thing.reader
	
	count = int(args.count) if args.count is not None else None
	sender = args.sender
	dest = int(args.dest) if args.dest is not None else None
	period = float(args.period) if args.period is not None else .001

	start = None

	def failed(reason):
		print reason

	if sender:

		def writeThing():
			# print 'hello'
			# log.msg('hello')
			if thing.writes == count:
				d = myCom.stop()
				d.addCallbacks(lambda res: reactor.stop(), failed)
			else:
				toSend = args.message if args.message is not None else 'hello'
				d = myCom.write(toSend, dest)
				d.addCallback(lambda res: thing.writeRes())
				d.addCallbacks(lambda res: reactor.callLater(period, writeThing),lambda res: reactor.callLater(period, writeThing))

			return d

		d = myCom.start()
		thing.start = time.time()
		d.addCallbacks(lambda res: reactor.callLater(period, writeThing), failed)
	else:

		def check():
			if thing.last == thing.read:
				d = myCom.stop()
				d.addCallback(lambda res: thing.printRes())
				d.addCallbacks(lambda res: reactor.stop(), failed)
			else:
				thing.last = thing.read
				reactor.callLater(period, check)

		d = myCom.start()
		d.addCallbacks(lambda res: reactor.callLater(period, check), failed)

	reactor.run()
	if sender:
		print "sent %d messages in %f seconds" % (thing.writes, thing.lastTime - thing.start)
		print "payload throughput: %f bytes per second" % ((thing.writes * len(args.message)) / (thing.lastTime - thing.start))
		with open('run.txt', 'w') as f:
			f.write("%f" % (thing.lastTime - thing.start))
#

if __name__ == "__main__":
	main()