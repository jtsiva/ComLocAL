#!/usr/bin/python

from __future__ import print_function
from twisted.protocols import basic
from twisted.internet import reactor
import time
import json

#debug
import sys


class IOHandler(basic.LineReceiver):
	def __init__(self, frame_size):
		self.__buffer = ""
		self.frame_size = frame_size #FRAME SIZE HERE
		self.writeHandler = None
		self.bytesReceived = 0
		self.bytesSent = 0
		self.last = 0
		self.reads = 0
		self.writes = 0
		self.start = None
		self.lastTime = None
		self.pendingFlush = None
		self.stopHandler = None
		self.empty = False

	def connectionMade(self):
		pass

	def connectionLost(self, reason):
		if self.stopHandler:
			self.stopHandler(reason)

	def rawDataReceived(self, data):
		now = time.time()
		if 0 == self.writes:
			self.start = now

		#we have new data, so wait to flush the buffer
		if self.pendingFlush is not None:
			self.pendingFlush.cancel()
			self.pendingFlush = None

		self.__buffer = self.__buffer + data
		frame_size = self.frame_size
		while len(self.__buffer) >= frame_size:
			self.frameReceived(self.__buffer[0:frame_size])
			self.__buffer = self.__buffer[frame_size:]

		#if we have leftover bytes, wait twice as long as the average time per packet
		#then send a partial packet
		#print (self.__buffer)
		self.empty = 0 == len(self.__buffer)
		if not self.empty:
			waitTime = (2 * (time.time() - self.start) / self.writes) if self.writes else .0001
			self.pendingFlush = reactor.callLater(waitTime, self.flushBuffer)

	def flushBuffer(self):
		def markCleared (result):
			self.__buffer = ""
			self.empty = 0 == len(self.__buffer)

		d = self.frameReceived(self.__buffer)
		d.addCallback(markCleared)
		return d


	def frameReceived(self,data):
		now = time.time()

		self.lastTime = now

		def countWrite(result):
			if result is not None and 'failure' not in result['result']:
				self.writes += 1
				self.bytesSent += len(data)
			elif result is not None:
				print ("failure:" + str(result), file=sys.stderr)

		def badWrite(reason):
			print(reason, file=sys.stderr)
		
		d = self.writeHandler(data)
		d.addCallbacks(countWrite, badWrite)
		return d

			
	def readHandler(self, data):
		now = time.time()
		self.bytesReceived += len(data['msg'])
		if 0 == self.reads:
			self.start = now

		self.reads += 1
		self.lastTime = now
		print(data['msg'], end='')

	def printStats(self):
		if self.bytesSent:
			print('Sent %d bytes in %f seconds' % (self.bytesSent, self.lastTime - self.start))
			print('%d writes' % self.writes)

		if self.bytesReceived:
			print('Received %d bytes in %f seconds' % (self.bytesReceived, self.lastTime - self.start))
			print('%d reads' % self.reads)