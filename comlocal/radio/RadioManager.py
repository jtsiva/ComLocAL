from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import json

class RadioManager (DatagramProtocol):
	def __init__(self):
		self._radioReg = {}

	def handleCmd (self, cmd):
		if 'get_radios' == cmd['cmd']:
			cmd['result'] = self._radioReg
		elif 'register' == cmd['cmd']:
			try:
				name = cmd['name']
				props = cmd['props'] #minimally should contain port
				self._radioReg[name] = props
				cmd['result'] = 'success'
			except KeyError:
				cmd['result'] = 'failed'
		elif 'unregister' == cmd['cmd']:
			try:
				del self._radioReg[cmd['name']]
				cmd['result'] = 'success'
			except KeyError:
				cmd['result'] = 'failed'
		else:
			cmd['result'] = "failed: no command %s" % (cmd['cmd'])

		return json.dumps(cmd)

	def datagramReceived(self, data, (host, port)):
		message = json.loads(data)
		if 'msg' == message['type']:
			response = data
			
		elif 'cmd' == message['type']:
			response = self.handleCmd(message)

		self.transport.write(response, (host,port))


reactor.listenUDP(10247, RadioManager(), interface="127.0.0.1")
reactor.run()