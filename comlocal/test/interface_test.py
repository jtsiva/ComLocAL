from comlocal.interface import ComLocALIFace


class myThing(object):
	def __init__(self):
		self.read = 0
		self.cmdRes = 0
		self.writeRes = 0

	def reader(self, msg):
		print msg
		self.read += 1

	def result(self, msg):
		print msg
		if 'cmd' in msg:
			self.cmdRes += 1
		elif 'msg' in msg:
			self.writeRes += 1

def formatMsg(msg,dest):
	return {'type':'msg','msg':msg,'dest':dest}

def formatCmd(cmd):
	return {'type':'cmd','cmd':cmd}

def main():
	thing = myThing()
	myCom = ComLocALIFace.ComLocAL('DRON')
	myCom.setReadCB (thing.reader)
	myCom.setResultCB (thing.result)

	try:
		myCom.start()
		while True:
			things = raw_input('> ')
			#pdb.set_trace()
			myCom.comWrite(formatMsg(things, 5))
	except KeyboardInterrupt:
		print ''
	except Exception as e:
		print e

	print 'reads: %i, writes: %i, cmd: %i' % (thing.read, thing.writeRes, thing.cmdRes)



if __name__ == "__main__":
	main()