#!/usr/bin/python

from comlocal.interface import ComLocALIFace
import sys
import time

#last = None

class myThing(object):
	def __init__(self):
		self.read = 0
		self.cmdRes = 0
		self.writeRes = 0
		self.readyToSend = False

	def reader(self, msg):
		#print msg
		self.read += 1
		readyToSend = True

	def result(self, msg):
		#print msg
		if 'cmd' in msg:
			self.cmdRes += 1
		elif 'msg' in msg:
			#last = time.time()
			self.writeRes += 1

def main():
	thing = myThing()
	myCom = ComLocALIFace.ComLocAL('TEST')
	myCom.setReadCB (thing.reader)
	myCom.setResultCB (thing.result)

	count = 1000 if len(sys.argv) < 2 else int(sys.argv[1])

	msg = {'type':'msg','msg':'hello'}

	try:
		myCom.start()

		while count > thing.writeRes:
			if thing.readyToSend:# or (time.time() - last) > 3:
				myCom.comWrite(msg)
	except KeyboardInterrupt:
		print ''
	except Exception as e:
		print e

	print 'reads: %i, writes: %i, cmd: %i' % (thing.read, thing.writeRes, thing.cmdRes)


#

if __name__ == "__main__":
	main()