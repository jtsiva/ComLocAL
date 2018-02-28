from comlocal.util.NetworkLayer import NetworkLayer
import time
import json

class RadioBuilder:
	def build(name):
		module = importlib.import_module('comlocal.radio.' + name + 'Manager')
		manager = getattr(module, name+'Manager')
		transport = getattr(module, name + 'Transport')
		start = getattr(module, 'startTransport')

		mgr = manager()
		trans = transport()
		mgr.setTransport(trans)
		trans.setManager(mgr)

		port = start(trans)

		return type('Radio', (object,),{'name':name,'mgr':mgr,'trans':trans,'port':port})


class ConnectionLayer(NetworkLayer):
	"""
	This class is responsible for maintaining connections 
	(and managing the state of the hardware?)

	"""

	def __init__(self, commonData):
		NetworkLayer.__init__(self, 'CL')
		self._commonData = commonData
		self.radios = []
		self.checkRadios() #weed out any radios that are not *actually* active
		
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection'] = {'pings' : 0, 'sent': 0, 'received' : 0}
	#

	def checkRadios(self):
		"""
		Check if radios are properly functioning
		TODO: implement
		"""
		pass
	#

	def runConnectionPolicy(self):
		for radio in radios:
			for cxn in radio.mgr.connections:
				pass

	def addRadio(self, name):
		try:
			rad = RadioBuilder.build(name)
			rad.mgr.setReadCB(self.read)
			self.radios.append(rad)
		except AttributeError:
			#invalid name
			pass
		except Exception as e:
			#maybe trying to start more than one of a given type
			pass

	# def removeRadio(self, name):
	# 	#LOCK
	# 	self.radios.remove(name)
	# 	#UNLOCK



	def getRadioNames(self):
		return [rad.name for rad in self.radios]

	#USED BY COM RADIO SETUP

	# def isRadio (self, port):
	# 	#LOCK
	# 	for radio in self.radios:
	# 		if radio._port == port:
	# 			return True
	# 	#UNLOCK

	# 	return False


	#connection management functions - higher level operations
	def ping(self, extra = None):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['pings'] += 1

		if extra is not None:
			extraData.update(extra)

		for radio in self.radios:
			radio.mgr.write(extraData)

	def handlePing(self, msg):
		#do things
		pass

	def read(self, msg):
		"""
		Count total messages received and callback

		TODO: exception handling for broken things
		"""
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['received'] += 1
		
		#


		"""

		update any other properties for connection

		track multihop connections here?

		0---1---2
		if 0 is us then we have a connection with 1 AND 2

		connection maintenance messages?

		"""
		if 'ping' in msg:
			self.handlePing(msg)
		else:
			self.readCB(msg)
	#

	def cmd(self, cmd):
		if 'get_connections' cmd['cmd']:
			connections = {}
			#aggregate all connections
			for radio in self.radios:
				for cxn in radio.mgr.connections:
					connections[cxn] = radio.mgr.connections[cxn]

			cmd['result'] = connections
		else:
			cmd['result'] = self.failure("unrecognized command %s" % cmd['cmd'])
		return cmd

	def write(self, msg):
		"""
		Write msg to radios

		"""
		
		try:

			if 'cmd' in msg:
				return self.cmd(msg)
				
			ret = []

			for radioName, addr in msg['radios']:
				for radio in self.radios:
					if radioName == radio.name:
						msg['addr'] = addr

						if self._commonData['logging']['inUse']:
							self._commonData['logging']['connection']['sent'] += 1
						#

						ret.append(radio.write(msg))
						
					#
				#
			# 	
			return ret
		except Exception as e:
			msg['result'] = self.failure(str(e))

		return msg

		








#