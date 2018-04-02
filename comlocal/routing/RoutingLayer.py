from comlocal.util.NetworkLayer import NetworkLayer
import networkx as nx
import json
import time


class RoutingLayer(NetworkLayer):
	def __init__(self, commonData):
		NetworkLayer.__init__(self, 'RL')
		self._commonData = commonData
		self._costFunction = self.defaultCost
		self._networkGraph = nx.MultiGraph()

		self._networkGraph.add_node(self._commonData['id'], root=True)

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing'] = {'pingsRcv' : 0, 'msgSnt': 0, 'msgRcv' : 0, 'cmdRcv' : 0, 'entriesDel' : 0, 'entriesAdd' : 0, 'fwd': 0}
	
	def defaultCost (self, graph):
		return 1.0

	def callCostFunc (self):
		#LOCK
		self._costFunction(self._networkGraph.copy(as_view=True))
		#UNLOCK

	def read(self, data):
		"""
		To be used as a callback
		data is from the previous layer to handle the read

		"""
		if self._needsForward(data):
			self._handleForward(data)
		else:
			if self._commonData['logging']['inUse']:
				self._commonData['logging']['routing']['msgRcv'] += 1
			self.readCB(data)


	def addLink(self, id1, id2, rad, addr):
		#LOCK
		self._networkGraph.add_edge(id1, id2, radio=rad, 
				address=addr, time=0, 
				weight=self.defaultCost(None))
		#UNLOCK

	def removeLink (self, rad, addr):
		#LOCK
		pass
		#UNLOCK

	def addNode (self, theID):
		#LOCK
		self._networkGraph.add_node(theID, root=False)
		#UNLOCK

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['entriesAdd'] += 1
		


	def _handlePing(self, msg):
		"""
		Use the ping to update the routing table
		
		"""

		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['pingsRcv'] += 1

		self._updateRoutingTable(msg)
	#

	def _isPing(self, msg):
		try:
			return 'ping' in msg
		except KeyError:
			return False
	#

	def setCostFunction (self, costFunction):
		self._costFunction = costFunction

	def _updateRoutingTable(self, msg):
		"""
		Update the network graph based on information from
		the message. ASSUMES that msg has already been checked
		for validity
		"""

		#TODO: expand to handle adding whole paths or updating from
		#another node's network graph

		#LOCK
		if msg['src'] not in self._networkGraph:
			self.addNode (msg['src'])

		if msg['radio'] not in self._networkGraph.edges([self._commonData['id'], msg['src']]):
			self.addLink(self._commonData['id'], msg['src'], msg['radio'],msg['sentby'])


		self._networkGraph.edges[self._commonData['id'], msg['src']]['time'] = time.time()
		self._networkGraph.edges[self._commonData['id'], msg['src']]['weight'] = self.callCostFunc()
		#UNLOCK
	#

	def _needsForward(self, msg):
		"""
		Check if the message is intended for this node or not
		"""
		try:
			return msg['dest'] != self._commonData['id'] and msg['src'] != self._commonData['id']
		except KeyError:
			return False
	#

	def _handleForward(self, msg):
		if self._commonData['logging']['inUse']:
			self._commonData['logging']['routing']['fwd'] += 1
		self.write(msg)
	#

	def _route(self, msg):
		"""
		Determine route/radio to use. This information is added to the msg
		
		TODO: add actual routing algorithms here
		"""
		if 'src' not in msg:
			msg['src'] = self._commonData['id']

		#https://stackoverflow.com/questions/15644684/best-practices-for-querying-graphs-by-edge-and-node-attributes-in-networkx
		#red = ((u,v) for u,v,d in G.edges(data=True) if d['color']=='red')
		radioList = []
		#LOCK
		for radio in msg['radios']:
			radioList += ([d['radio'], d['address']] for u,v,d in self._networkGraph.edges(data=True) if d['radio'] == radio)
		#UNLOCK

		msg['radios'] = radioList

		return msg


	def write(self, msg):
		try:
			if "cmd" in msg:
				if msg['cmd'] == 'get_neighbors':
					#LOCK
					msg['result'] = self._networkGraph.neighbors(self._commonData['id'])
					#UNLOCK
					return msg
				else:
					return self.writeCB(msg)
			else:
				if self._commonData['logging']['inUse']:
					self._commonData['logging']['routing']['msgSnt'] += 1
				return self.writeCB(self._route(msg))
		except Exception as e:
			msg['result'] = self.failure(str(e))
			return msg
	#
#