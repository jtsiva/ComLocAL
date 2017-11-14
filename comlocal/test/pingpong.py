#!/usr/bin/python

from comlocal.core import Com 
import json
import sys
import pdb
import time

def readHandler(msg):
	readHandler.count += 1
	readHandler.go = True
	print json.dumps(msg, sort_keys=True, indent=4, separators=(',', ': '))

def main():
	com = Com.Com()
	readHandler.count = 0
	readHandler.go = False
	com.setReadHandler(readHandler)
	com.start()

	try:

		#set up read callback

		pings = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

		msg = json.loads('{"type":"msg"}')
		while pings > 0:
			if readHandler.go: #don't send unless we've received
				msg['payload'] =  pings
				com.write(msg)
				pings -= 1
				readHandler.go = False
			else:
				time.sleep(0)
		#

		while True:
			pass
	except KeyboardInterrupt:
		pass
	finally:
		com.stop()

	print readHandler.count


#

if __name__ == "__main__":
	#pdb.set_trace()
	main()