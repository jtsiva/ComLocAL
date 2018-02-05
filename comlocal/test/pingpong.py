#!/usr/bin/python

from comlocal.interface import ComLocALIFace
import time
import argparse

last = time.time()
sender = True
txAck = True

class myThing(object):
	def __init__(self):
		self.read = 0
		self.cmdRes = 0
		self.writeRes = 0

	def reader(self, msg):
		
		self.read += 1
		if self.read % 100 == 0:
			print msg
		sender = True
		
		

	def result(self, msg):
		#print msg
		if 'cmd' in msg:
			self.cmdRes += 1
		elif 'msg' in msg:
			txAck = True
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
	sender = args.first
	dest = int(args.dest)

	msg = {'type':'msg','msg':'hello','dest':dest}

	try:
		last = time.time()
		myCom.start()
		writes = 0

		while count > writes:
			if sender or (not txAck and (time.time() - last) > .5):
				myCom.comWrite(msg)
				txAck = False
				writes += 1
				sender = False
				last = time.time()
	except KeyboardInterrupt:
		print ''
	except Exception as e:
		print e

	print 'reads: %i, writes: %i, cmd: %i' % (thing.read, writes, thing.cmdRes)


#

if __name__ == "__main__":

	main()