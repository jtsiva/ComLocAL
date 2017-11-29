from comlocal.util import Properties
import Radio
import json
import bluetooth
import bluetooth._bluetooth as _bt
import struct
import socket
import errno
import threading
import Queue
import pdb


class Bluetooth (Radio.Radio):
	"""
	Abstracts all communication over Bluetooth / BLE

	All communication is broadcast
	"""
	def __init__ (self):
		super(Bluetooth, self).__init__(self._setupProperties())
		self._name = 'BT'
		self._port = 0x2807 #10247
		self._sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)

		self._sock.bind(("", self._port))
		self._sock.listen(5) #allow multiple connections

		self._readQ = Queue.Queue()
		
	#

	def __del__(self):
		self._sock.close()

	def start(self):
		self._threadRunning = True
		self._readThread = threading.Thread(target=self._backgroundRead)

	def stop(self):
		self._threadRunning = False
		self._readThread.join()


	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		props = Properties.Properties()
		props.addr = self._getAddress()
		props.maxPacketLength = 1024
		props.costPerByte = 1

		return props
	#

	def _getAddress(self):
		get_byte = ord
		hci_sock = _bt.hci_open_dev(0)
		old_filter = hci_sock.getsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, 14)
		flt = _bt.hci_filter_new()
		opcode = _bt.cmd_opcode_pack(_bt.OGF_INFO_PARAM, 
					_bt.OCF_READ_BD_ADDR)
		_bt.hci_filter_set_ptype(flt, _bt.HCI_EVENT_PKT)
		_bt.hci_filter_set_event(flt, _bt.EVT_CMD_COMPLETE);
		_bt.hci_filter_set_opcode(flt, opcode)
		hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, flt )

		_bt.hci_send_cmd(hci_sock, _bt.OGF_INFO_PARAM, _bt.OCF_READ_BD_ADDR )

		pkt = hci_sock.recv(255)

		status,raw_bdaddr = struct.unpack("xxxxxxB6s", pkt)
		assert status == 0

		t = [ "%X" % get_byte(b) for b in raw_bdaddr ]
		t.reverse()
		bdaddr = ":".join(t)

		# restore old filter
		hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, old_filter )
		return bdaddr

	def _backgroundRead(self):
		while self._threadRunning:
			client_sock = None
			try:
				client_sock,address = self._sock.accept()
				data = client_sock.recv(self.getProperties().maxPacketLength)
				tmp = json.loads(data)
				tmp['sentby'] = address[0] #want the address

				self._readQ.put(tmp)
			finally:
				if client_sock is not None:
					client_sock.close()
		#
	#

	def read(self):
		"""
		Read from radio and return json object

		Non blocking
		"""
		
		try:
			data = self._readQ.get_nowait()
		except Queue.Empty:
			data = {}

		return data
	#

	def write(self, data):
		"""
		write json object to radio
		"""

		#discover devices
		#bluetooth.set_packet_timeout( bdaddr, timeout)
		#connect and send to everyone!
		nearbyDevices = bluetooth.discover_devices(duration=2)

		try:
			for addr in nearbyDevices:
				self._sock.connect((addr, self._port))
				self._sock.send(json.dumps(data))		
		except Exception as e:
			raise e
		#
	#
#