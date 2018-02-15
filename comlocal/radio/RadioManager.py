
from twisted.spread import pb
from twisted.python import log

from comlocal.util.NetworkLayer import NetworkLayer

class RadioManager (pb.Root, NetworkLayer):
	myPort = 10247

	def __init__ (self):
		self._radioReg = {}
		NetworkLayer.__init__(self, 'RadMgr')

	def remote_cmd(self, cmd):
		log.msg (cmd)

		if 'cmd' in cmd:
			if 'get_radios' == cmd['cmd']:
				cmd['result'] = self._radioReg
			elif 'reg_radio' == cmd['cmd']:
				try:
					name = cmd['name']
					props = cmd['props'] #minimally should contain port
					self._radioReg[name] = props
					cmd['result'] = self.success('')
				except KeyError:
					cmd['result'] = self.failure("missing attributes in props")
			elif 'unreg_radio' == cmd['cmd']:
				try:
					self._radioReg.pop(cmd['name'])
					cmd['result'] = self.success('')
				except KeyError:
					cmd['result'] = self.failure('no radio to remove')
			else:
				cmd['result'] = self.failure("no command %s" % (cmd['cmd']))
		else:
			cmd['result'] = self.failure ("no command given")

		return cmd

	def remote_write(self, data):
		return data
