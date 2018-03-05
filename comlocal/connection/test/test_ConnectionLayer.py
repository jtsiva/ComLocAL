from twisted.trial.unittest import TestCase
from twisted.internet.task import deferLater
from twisted.internet import reactor

from comlocal.connection.ConnectionLayer import ConnectionLayer



class Frame:
	def __init__(self):
		self.hit = False
		self.msg = None

	def read(self, message):
		self.hit = True
		self.msg = message

	def write(self, message, addr):
		self.hit = True


class ConnectionLayerTestCase(TestCase):
	def setUp(self):
		self.cl = ConnectionLayer({'logging':{'inUse':False}, 'id':1})
		self.frame = Frame()

	def tearDown(self):
		self.cl.cleanupRadios()

	def test_addLoopback(self):
		self.cl.addRadio('Loopback')
		self.assertTrue(len(self.cl.radios) > 0)

	def test_addLoopbackTwice(self):
		self.cl.addRadio('Loopback')
		try:
			self.cl.addRadio('Loopback')
			self.assertTrue(False)
		except ValueError:
			self.assertTrue(True)


	def test_addBadRadio(self):
		self.cl.addRadio('Thing')
		self.assertTrue(len(self.cl.radios) == 0)


	def test_addLoopbackAndWiFi(self):
		self.cl.addRadio('Loopback')
		self.cl.addRadio('WiFi')
		self.assertTrue(len(self.cl.radios) == 2)

	def test_getRadioNames(self):
		self.cl.addRadio('Loopback')
		self.cl.addRadio('WiFi')
		names = self.cl.getRadioNames()
		self.assertTrue('Loopback' in names and 'WiFi' in names)

	def test_readCB(self):
		self.cl.addRadio('Loopback')
		self.cl.setReadCB(self.frame.read)
		self.cl.radios[0].write({"msg":"hello", "addr":"<loopback>"})
		self.assertTrue(self.frame.hit)

	def test_writeLoopback(self):
		self.cl.addRadio('Loopback')
		self.cl.setReadCB(self.frame.read)
		self.cl.write({"msg":"hello", "radios":[("Loopback", "<loopback>")]})
		self.assertTrue(self.frame.hit)

	def test_writeWiFi(self):
		def blah():
			self.assertTrue(self.frame.hit)

		self.cl.addRadio('WiFi')
		self.cl.setReadCB(self.frame.read)
		self.cl.write({"msg":"hello", "radios":[("WiFi", "127.0.0.1")]})
		d=deferLater(reactor, .1, blah)
		return d
		

	def test_writeLoopbackAndWiFi(self):
		self.cl.addRadio('Loopback')
		self.cl.addRadio('WiFi')
		self.cl.setReadCB(self.frame.read)
		self.cl.write({"msg":"hello", "radios":[("Loopback", "<loopback>"), ("WiFi", "127.0.0.1")]})
		self.assertTrue(self.frame.hit)

	def test_cmdGetConnectionsEmpty(self):
		self.cl.addRadio('Loopback')
		cnxs =  self.cl.write({"cmd":"get_connections"})['result']
		self.assertTrue(not cnxs)

	def test_cmdGetConnectionsSelf(self):
		self.cl.addRadio('Loopback')
		self.cl.setReadCB(self.frame.read)
		self.cl.write({"msg":"hello", "radios":[("Loopback", "<loopback>")]})
		cnxs =  self.cl.write({"cmd":"get_connections"})['result']
		self.assertTrue(len(cnxs) == 1 and self.frame.hit)

	def test_cmdGetConnectionsWiFiAndLoopback(self):
		def blah():
			cnxs =  self.cl.write({"cmd":"get_connections"})['result']
			self.assertTrue(len(cnxs) == 2 and self.frame.hit)

		self.cl.addRadio('Loopback')
		self.cl.addRadio('WiFi')
		self.cl.setReadCB(self.frame.read)
		self.cl.write({"msg":"hello", "radios":[("Loopback", "<loopback>"), ("WiFi", "127.0.0.1")]})
		
		d=deferLater(reactor, .1, blah)
		return d

	def test_cmdPing(self):
		self.cl.addRadio('Loopback')
		self.cl.write({"cmd":"ping"})
		self.assertTrue(self.cl.pings == 1)

	def test_cmdPingWithExtra(self):
		self.cl.addRadio('Loopback')
		self.cl.write({"cmd":"ping", "extra":"other stuff"})
		self.assertTrue(self.cl.pings == 1)

	def test_cmdCheckRadios(self):
		self.cl.addRadio('Loopback')
		self.cl.addRadio('WiFi')
		res = self.cl.write({"cmd":"check_radios"})['result']
		for entry in res:
			self.assertTrue(entry['running'])
