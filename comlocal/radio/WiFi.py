
from util import Properties
import Radio
import socket
import struct
import fcntl
import sys
import subprocess

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

	UPDATE (10-10-17): all ad-hoc mode communication
		need to scan for other devices in range
		can both unicast and broadcast since there is no need to
		broadcast if the destination is a 1-hop neighbor

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

		props.maxPacketLength = 512
		props.costPerByte = 1

		return props

	def read(self, n):
		"""
		Read n bytes

		return n bytes or whatever is available to read (which is smaller)
		"""
		try:
			data, server = self._rSock.recvfrom(n)
		except socket.timeout:
			data = []

		return data

	def write(self, dest, data):
		"""
		Write data bytes. Dest is expected to be a 4 byte list

		return number of bytes written
		"""
		fDest = ''
		for e in dest:
			fDest += str(e) + '.'

		fDest = fDest[:-1]
		sent = self._wSock.sendto(data, (fDest, self._port))

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
		Get list of IP addresses for 1 hop neighbors
		Can discover all 1-hop neighbors by using nmap

		Return list if successful, empty list otherwise
		TODO: define exception to be thrown to differentiate between failure
		and no neighbors (10/18/17)
		"""
		try:
			addrToSearch = self.getProperties().addr[:7] + '0/24'
			output = subprocess.check_output("nmap -n -sn " + addrToSearch + " -oG - | awk '/Up$/{print $2}'", shell=True)
			neighbors = output.split()
		except subprocess.CalledProcessError:
			neighbors = []

		#TODO: remove self from nb, use to detect fail?

		return neighbors

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
