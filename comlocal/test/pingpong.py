#!/usr/bin/python

from comlocal.interface import ComLocALIFace
import time
import argparse

last = time.time()
readyToSend = True

class myThing(object):
	def __init__(self):
		self.read = 0
		self.cmdRes = 0
		self.writeRes = 0
		self.readyToSend = False

	def reader(self, msg):
		readyToSend = True
		self.read += 1
		if self.read % 100 == 0:
			print msg
		

	def result(self, msg):
		#print msg
		if 'cmd' in msg:
			self.cmdRes += 1
		elif 'msg' in msg:
			last = time.time()
			self.writeRes += 1

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-c", "--count", required = True, help="set the number messages that sender should send")
	parser.add_argument ("-f", "--first", action="store_true", default=False, help="set whether this device will send first")
	parser.add_argument ("-d", "--dest", required = True, help="set the destination for the message")


	args =  parser.parse_args()

	thing = myThing()
	myCom = ComLocALIFace.ComLocAL('TEST')
	myCom.setReadCB (thing.reader)
	myCom.setResultCB (thing.result)

	count = int(args.count)
	readyToSend = args.first
	dest = int(args.dest)

	msg = {'type':'msg','msg':'hello','dest':dest}

	try:
		last = time.time()
		myCom.start()
		writes = 0

		while count > writes:
			if readyToSend or (time.time() - last) > .5:
				myCom.comWrite(msg)
				writes += 1
				readyToSend = False
				last = time.time()
	except KeyboardInterrupt:
		print ''
	except Exception as e:
		print e

	print 'reads: %i, writes: %i, cmd: %i' % (thing.read, thing.writeRes, thing.cmdRes)


#

if __name__ == "__main__":

	main()