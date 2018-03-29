#!/usr/bin/python

from comlocal.radio.Dummy import Dummy
from twisted.spread import pb
from twisted.internet import reactor
import argparse
import time
import json

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-m", "--message", required = True, help="data to be sent")
	parser.add_argument ("-c", "--count", required=True, help="how many copies of message to send")

	args =  parser.parse_args()

	i = 0

	time.sleep(1.0)

	while i < int(args.count):
		def regAck(result):
			pass#print result

		def regNack(reason):
			print 'rawr!'

		def connected(obj):
			d = obj.callRemote('read', json.loads(args.message))
			d.addCallbacks(regAck,regNack)
			d.addCallback(lambda result: obj.broker.transport.loseConnection())
			return d

		def failed(reason):
			log.msg(reason)

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", Dummy.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)
		i+=1

	reactor.run()


if __name__ == '__main__':
	main()