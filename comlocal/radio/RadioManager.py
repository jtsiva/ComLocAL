from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory, DatagramProtocol
from twisted.python import log
import json

class RadioManagerProtocol (DatagramProtocol):
	def __init__(self, service):
		self._service = service

	def datagramReceived(self, data, (host, port)):
		message = json.loads(data)
		if 'msg' == message['type']:
			response = data
			
		elif 'cmd' == message['type']:
			response = self._service.handleCmd(message)

		self.transport.write(response, (host,port))


class RadioManagerService(service.Service):
	def __init__ (self, authFile=None):
		self._radioReg = {}
		self.authFile = authFile

	def startService (self):
		service.Service.startService(self)
		if self.authFile is not None:
			self.authKey = open(self.authFile).read()
			log.msg('loaded auth key from: %s' % (self.authFile,))
		else:
			log.msg ('no file from which to load auth key')

	def isAuthorized (self, toCheck):
		return True

	def handleCmd (self, cmd):
		if self.isAuthorized('blah'):
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
		else:
			cmd['result'] = "failed: not authorized"

		return json.dumps(cmd)

port = 10247
iface = '127.0.0.1'
authFile = ''

topService = service.MultiService()
radioManagerService = RadioManagerService()
radioManagerService.setServiceParent(topService)

udpService = internet.UDPServer(port, RadioManagerProtocol(radioManagerService), interface=iface)
udpService.setServiceParent(topService)

application = service.Application('radiomanager')
topService.setServiceParent(application)