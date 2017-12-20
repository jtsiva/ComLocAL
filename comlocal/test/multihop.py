#!/usr/bin/python
from comlocal.core import Com
import time
import argparse
import json

def readHandler(msg):
	print json.dumps(msg)

def main():
	print 'should be set as: 1-sender (BT|WiFi), 2-forwarder (BT & WiFi), 3-listener (WiFi|BT)'
	parser = argparse.ArgumentParser()
	parser.add_argument ("-r", "--role", required = True, help="set the role for this device ('sender', 'forwarder', 'listener')")
	parser.add_argument ("-c", "--count", help="set the number messages that sender should send")

	args =  parser.parse_args()

	com = Com.Com(log=True, configFile='default.conf')

	try:
		if args.role == 'sender':
			com.start()
			cnt = args.count if args.count is not None else 100
			for i in range(cnt):
				com.write(json.loads('{"type" : "msg", "dest" : 3, "payload" : "hello"}'))
			#
		#	
		elif args.role == 'forwarder':
			com.start()
			time.sleep(30)
		elif args.role == 'listener':
			com.setReadHandler(readHandler)
			com.start()
			time.sleep(30)
			
	finally:
		com.stop()



if __name__ == "__main__":
	main()