#!/usr/bin/python

from comlocal.radio.Dummy import Dummy
from twisted.spread import pb
import argparse
import time

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-m", "--message", required = True, help="data to be sent")
	parser.add_argument ("-t", "--time", help="how many seconds the data should be sent for")

	args =  parser.parse_args()

	start = time.time()

	while time.time() - start < args.time:
		def regAck(result):
			pass

		def regNack(reason):
			print 'rawr!'

		def connected(obj):
			d = obj.callRemote('read', args.message)
			d.addCallbacks(regAck,regNack)
			d.addCallback(lambda result: obj.broker.transport.loseConnection())
			return d

		def failed(reason):
			log.msg(reason)

		factory = pb.PBClientFactory()
		reactor.connectTCP("127.0.0.1", Dummy.myPort, factory)
		d = factory.getRootObject()
		d.addCallbacks(connected, failed)


if __name__ == '__main__':
	main()