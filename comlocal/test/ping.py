#!/usr/bin/python

from comlocal.core import Com 
import sys

def main():
	com = Com.Com()

	#set up read callback

	pings = int(sys.argv[1])

	msg = json.loads('{"type":"msg"}')
	while pings > 0:
		msg['payload'] =  pings
		com.write(msg)
		pings -= 1
	#

	try:
		while True:
			pass
	except KeyboardInterrupt:
		break


#

if __name__ == "__main__":
	main()