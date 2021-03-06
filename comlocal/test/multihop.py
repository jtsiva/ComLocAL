#!/usr/bin/python
from comlocal.core import Com
import time
import argparse
import json
#debug only!
import yappi

def readHandler(msg):
	print json.dumps(msg)

def main():
	print 'should be set as: 1-sender (BT|WiFi), 2-forwarder (BT & WiFi), 3-listener (WiFi|BT)'
	parser = argparse.ArgumentParser()
	parser.add_argument ("-r", "--role", required = True, help="set the role for this device ('sender', 'forwarder', 'listener')")
	parser.add_argument ("-c", "--count", help="set the number messages that sender should send")
	parser.add_argument ("-d", "--delay", help="set delay in seconds (float) between messages")

	args =  parser.parse_args()

	com = Com.Com(log=True, configFile='default.conf')

	try:
		if args.role == 'sender':
			com.start()
			cnt = int(args.count) if args.count is not None else 100
			delay = float(args.delay) if args.delay is not None else 0
			for i in range(cnt):
				com.write(json.loads('{"type" : "msg", "dest" : 3, "msg" : "hello"}'))
				time.sleep(delay)
			#
		#	
		elif args.role == 'forwarder':
			com.start()
			time.sleep(360)

		elif args.role == 'listener':
			com.setReadHandler(readHandler)
			com.start()
			time.sleep(360)
			
	finally:
		com.stop()



if __name__ == "__main__":
	yappi.set_clock_type('cpu')
	yappi.start(builtins=True)
	main()
	funcStats = yappi.get_func_stats()
	threadStats = yappi.get_thread_stats()
	funcStats.save('callgrind.func.prof', type='callgrind')
	#threadStats.save('callgrind.thread.prof', type='callgrind')