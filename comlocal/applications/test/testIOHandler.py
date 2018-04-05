#!/usr/bin/python

from comlocal.applications import IOHandler

from twisted.internet import stdio
from twisted.internet import reactor

def main():
	ioThing = IOHandler.IOHandler()
	ioThing.setRawMode()
	stdio.StandardIO(ioThing)
	reactor.run()
	ioThing.printStats()

if __name__ == '__main__':
	main()