from comlocal.util.NetworkLayer import NetworkLayer
import time
import json
import importlib

class RadioBuilder:
	#https://stackoverflow.com/questions/12674080/what-is-the-most-efficient-way-to-dynamically-create-class-instances
	def build(self, name):
		module = importlib.import_module('comlocal.radio.' + name + 'Manager')
		manager = getattr(module, name+'Manager')
		transport = getattr(module, name + 'Transport')
		start = getattr(module, 'startTransport')

		mgr = manager()
		trans = transport()
		mgr.setTransport(trans)
		trans.setManager(mgr)

		port = start(trans)

		return type('Radio', (object,),{'name':name,'write':mgr.write, '_mgr':mgr,'_trans':trans,'port':port})


class ConnectionLayer(NetworkLayer):
	"""
	This class is responsible for maintaining connections 
	(and managing the state of the hardware?)

	"""

	def __init__(self, commonData):
		NetworkLayer.__init__(self, 'CL')
		self._commonData = commonData
		self.radios = []
		self.pings = 0 #temporary
		self._checkRadios() #weed out any radios that are not *actually* active
		
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection'] = {'pings' : 0, 'sent': 0, 'received' : 0}
	#

	def _checkRadios(self):
		"""
		Check if radios are properly functioning
		
		"""
		res = []
		for radio in self.radios:
			entry = {'name': radio.name}
			entry.update(radio._mgr.cmd({'cmd':'get_status'})['result'])
			res.append(entry)

		return res
	#

	def runConnectionPolicy(self):
		for radio in radios:
			for cnx in radio._mgr.connections:
				pass

	def addRadio(self, name):
		try:
			if name not in self.getRadioNames():
				rad = RadioBuilder().build(name)
				rad._mgr.setReadCB(self.read)
				self.radios.append(rad)
			else:
				raise ValueError("duplicate radio name '{0}' found".format(name))
		except ImportError as e:
			#invalid name
			#print 'invalid name ' + str(e)
			pass

	def cleanupRadios(self):
		for rad in self.radios:
			if rad.port is not None:
				port, rad.port = rad.port, None
				port.stopListening()

	def getRadioNames(self):
		return [rad.name for rad in self.radios]

	#connection management functions - higher level operations
	def _ping(self, extra = None):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['pings'] += 1

		message = {'ping':{'id':self._commonData['id']}}

		if extra is not None:
			message.update(extra)

	
		for radio in self.radios:
			props = radio._mgr.cmd({'cmd':'get_props'})['result']
			message['addr'] = props['bcastAddr']
			radio.write(message)
		
		return self.success('')

	def _handlePing(self, msg):
		"""
		update any other properties for connection

		track multihop connections here?

		0---1---2
		if 0 is us then we have a connection with 1 AND 2

		connection maintenance messages?

		"""
		self.pings+=1

	def read(self, msg):
		"""
		Count total messages received and callback

		TODO: exception handling for broken things
		"""
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['connection']['received'] += 1
		
		#

		if 'ping' in msg:
			self._handlePing(msg)
		else:
			self.readCB(msg)
	#

	def cmd(self, cmd):
		if 'get_connections' == cmd['cmd']:
			connections = {}
			#aggregate all connections
			for radio in self.radios:
				for cxn in radio._mgr.connections:
					connections[cxn] = radio._mgr.connections[cxn]

			cmd['result'] = connections
		elif 'ping' == cmd['cmd']:
			extra = None
			if 'extra' in cmd:
				extra = {}
				extra['extra'] = cmd['extra']
			res = self._ping(extra)
			cmd['result'] = res
		elif 'check_radios' == cmd['cmd']:
			cmd['result'] = self._checkRadios()
		elif 'get_radio_props' == cmd['cmd']:
			for radio in self.radios:
				if radio.name == cmd['name']:
					cmd['result'] = radio._mgr.cmd({'cmd':'get_props'})['result']
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
				
			radios = msg.pop('radios')
			message = msg.copy()
			message['result'] = []
			for radioName, addr in radios:
				for radio in self.radios:
					if radioName == radio.name:

						msg['addr'] = addr

						if self._commonData['logging']['inUse']:
							self._commonData['logging']['connection']['sent'] += 1
						#

						message['result'].append(radio.write(msg)['result'])
						
					#
				#
			# 	
			return message
		except Exception as e:
			msg['result'] = self.failure(str(e))

		return msg

		








#