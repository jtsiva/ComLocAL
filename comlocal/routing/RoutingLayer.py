from comlocal.util.NetworkLayer import NetworkLayer
import networkx as nx
import json
import time


class RoutingLayer(NetworkLayer):
	def __init__(self, commonData):
		self._commonData = commonData
		self._networkGraph = nx.MultiGraph()

		self._networkGraph.addNode(self._commonData['id'], root=True)

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing'] = {'pingsRcv' : 0, 'msgSnt': 0, 'msgRcv' : 0, 'cmdRcv' : 0, 'entriesDel' : 0, 'entriesAdd' : 0, 'fwd': 0}
		

	def read(self, data):
		"""
		To be used as a callback
		data is from the previous layer to handle the read

		"""
		if self._isPing(data):
			self._handlePing(data)
		elif self._needsForward(data):
			self._handleForward(data)
		else:
			if self._commonData['logging']['inUse']:
				self._commonData['logging']['routing']['msgRcv'] += 1
			self.readCB(data)


	def _ageTable(self):

		toDelete = {}

		for ID, radios in self._routingTable.iteritems():
			for radio, attr in radios.iteritems():
				if time.time() - attr['time'] > self._maxAge:
					toDelete[ID] = radio

		with self._tableLock:
			for ID, radio in toDelete.iteritems():
				del self._routingTable[ID][radio]
				if self._commonData['logging']['inUse']:
					self._commonData['logging']['routing']['entriesDel'] += 1

				if not self._routingTable[ID]:
					del self._routingTable[ID]

		if self._commonData['logging']['inUse']:
			logging.info('routing:' + self._getRoutes())

		if self._runAging:
			#reschedule for later only if runAging is true
			threading.Timer(self._agingDelay, self._ageTable).start()
		else:
			self._agingStopped = True
		#

	def _getRoutes(self):
		"""
		Return the routing table in a nice format

		DEBUG function
		"""
		return json.dumps(self._routingTable, sort_keys=True, indent=4, separators=(',', ': '))


	def _handlePing(self, msg):
		"""
		Use the ping to update the routing table
		
		"""
		#pdb.set_trace()

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['pingsRcv'] += 1
		self._updateRoutingTable(msg)

		return msg

	def _isPing(self, msg):
		try:
			return msg["type"] == "ping"
		except KeyError:
			return False

	def _updateRoutingTable(self, msg):
		"""
		Update the network graph based on information from
		the message. ASSUMES that msg has already been checked
		for validity
		"""

		#TODO: expand to handle adding whole paths or updating from
		#another node's network graph

		if msg['src'] not in self._networkGraph:
			self._routingTable.addNode(msg['src'], root=False)
			if self._commonData['logging']['inUse']:
				self._commonData['logging']['routing']['entriesAdd'] += 1

		if msg['radio'] not in self._networkGraph.edges():
			self._networkGraph.add_edge(self._commonData['id'], msg['src'], radio=msg['radio'], addr=msg['sentby'], time=0)

		self._networkGraph.edges[self._commonData['id'], msg['src']]['time'] = time.time()
	#

	def _needsForward(self, msg):
		"""
		Check if the message is intended for this node or not
		"""
		try:
			return msg['dest'] != self._commonData['id'] and msg['src'] != self._commonData['id']
		except KeyError:
			return False

	def _handleForward(self, msg):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['fwd'] += 1
		self.write(msg)

	def _route(self, msg):
		"""
		Determine route/radio to use. This information is added to the msg
		
		TODO: add actual routing algorithms here
		"""
		msg['src'] = self._commonData['id']

		#https://stackoverflow.com/questions/15644684/best-practices-for-querying-graphs-by-edge-and-node-attributes-in-networkx
		#red = ((u,v) for u,v,d in G.edges(data=True) if d['color']=='red')
		
		for radio in self._commonData['activeRadios']
			
		return msg

	def write(self, msg):
		if  msg['type'] == "cmd":
			if msg['cmd'] == 'getNeighbors':
				msg['result'] = self._networkGraph.neighbors(self._commonData['id'])
				return msg
			else:
				return self.writeCB(msg)
		else:
			if self._commonData['logging']['inUse']:
				self._commonData['logging']['routing']['msgSnt'] += 1
			return self.writeCB(self._route(msg))


	def _handleCommmand(self, msg):
		"""
		Pass message containing a command of to the appropriate
		callback
		"""
		try:
			self._cmdHandler(msg)
		except Exception as e:
			raise e
		finally:
			return msg

#