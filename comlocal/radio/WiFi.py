
from util import Properties
from radio import Radio
import socket
import struct
import fcntl
import sys

class WiFi (Radio.Radio):
	"""
	Facilitates / abstracts all communication over WiFi
	All communication is multicast UDP. The address within the packet
	is used to determine intended destination

	multicast addr: 224.0.0.0 - 239.255.255.255
	broadcast addr: 255.255.255.255

	multicast for infrastructure
	'broadcast' for ad hoc (each device addr based on unique UAV ID)

	multicast based on:
	https://pymotw.com/2/socket/multicast.html

	"""
	def __init__ (self):
		self._name = 'WiFi'
		super(WiFi, self).__init__(self._setupProperties())

		self._groupAddr = '224.0.2.47'
		self._port = 10000
		self._multicastGroup = (self._groupAddr, self._port)
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.settimeout(0.2)
		ttl = struct.pack('b', 1)
		self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	def __del__(self):
		self._sock.close()

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

		props.maxPacketLength = 512
		props.costPerByte = 1

		return props

	def read(self, n):
		"""
		Read n bytes

		return n bytes or whatever is available to read (which is smaller)
		"""
		try:
			data, server = self._sock.recvfrom(n)
		except socket.timeout:
			pass

		return data

	def write(self, data):
		"""
		Write data bytes

		return number of bytes written
		"""
		sent = self._sock.sendto(data, self._multicastGroup)

		return sent

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

	def scan(self):
		"""
		Send some sort of HELLO message to other radios listening for it.
		Think of this as the discovery protocol for a given radio.
		"""
		pass

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