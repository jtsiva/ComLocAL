
from comlocal.util import Properties
import Radio
import socket
import json

class WiFi (Radio.Radio):
	"""
	UPDATE (10-10-17): all ad-hoc mode communication
		need to scan for other devices in range
		
	UPDATE (11-9-17): only UDP broadcast implemented

	"""
	def __init__ (self):
		self._name = 'WiFi'
		super(WiFi, self).__init__(self._setupProperties())

		self._port = 10247
		self._rSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._wSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._rSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._wSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._wSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self._rSock.settimeout(.05)
		self._rSock.bind(('0.0.0.0', self._port))

		t = self._getProperties().addr.split('.')
		t[-1] = '255'
		self._broadcastAddr = ('.'.join(t), self._port)
	#

	def __del__(self):
		self._rSock.close()
		self._wSock.close()

	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		props = Properties.Properties()
		try:
			props.addr = self._get_ip_address('wlan0')
		except IOError:
			#my laptop has a different form
			props.addr = self._get_ip_address('wlp1s0')

		props.maxPacketLength = 4096
		props.costPerByte = 1

		return props

	def read(self):
		"""
		Read from radio and return json object

		Non blocking
		"""
		try:
			data = self._rSock.recv(self.getProperties().maxPacketLength)
		except socket.timeout:
			data = '{}'

		return json.loads(data)
	#

	def write(self, data):
		"""
		write json object to radio
		"""

		try:
			res = self._wSock.sendto(json.dumps(data), self._broadcastAddr)
		except Exception as e:
			raise e
		#
	#

	def _get_ip_address(self, ifname):
		"""
			Return ip address of interface:
			https://raspberrypi.stackexchange.com/questions/6714/how-to-get-the-raspberry-pis-ip-address-for-ssh
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,  # SIOCGIFADDR
			struct.pack('256s', ifname[:15])
		)[20:24])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   ---deal with this later---
#                   V                        V

	def range(self):
		"""
		Either define as a function of RSSI (determined empirically)
		or, in the case of UWB, just get the range from TWR. Return a
		tuple of (range, error) both in meters.
		"""
		pass

	def setPwrMode(self, mode):
		"""
		Set the power mode of the radio--intended to set the radio to
		a lower power mode
		"""
		pass
#
