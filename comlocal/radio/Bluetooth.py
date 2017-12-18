from comlocal.util import Properties
import Radio
import json
import bluetooth
import bluetooth._bluetooth as _bt
import struct
import socket
import errno
import threading
import subprocess
import os
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
from socket import (
    socket,
    AF_BLUETOOTH,
    SOCK_RAW,
    BTPROTO_HCI,
    SOL_HCI,
    HCI_FILTER,
)

import pdb


class Bluetooth (Radio.Radio):
	"""
	Abstracts all communication over Bluetooth / BLE

	All communication is broadcast
	"""
	def __init__ (self):
		super(Bluetooth, self).__init__(self._setupProperties())
		self._name = 'BT'

		btlib = find_library("bluetooth")
		if not btlib:
			raise Exception(
			    "Can't find required bluetooth libraries"
			    " (need to install bluez)"
			)
		self._bluez = CDLL(btlib, use_errno=True)

		dev_id = self._bluez.hci_get_route(None)

		self._sock = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)
		self._sock.bind((dev_id,))

		err = self._bluez.hci_le_set_scan_parameters(self._sock.fileno(), 0, 0x10, 0x10, 0, 0, 1000);
		if err < 0:
			raise Exception("Set scan parameters failed")
			# occurs when scanning is still enabled from previous call

		# allows LE advertising events
		hci_filter = struct.pack(
		    "<IQH", 
		    0x00000010, 
		    0x4000000000000000, 
		    0
		)
		self._sock.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)


		# self._port = 0x2807 #10247
		# self._sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)

		# self._sock.settimeout(.05)
		# self._sock.bind(("", self._port))
		# self._sock.listen(5) #allow multiple connections

		# self._readQ = Queue.Queue()
		# self._readThread = threading.Thread(target=self._backgroundRead)
		
	#

	def __del__(self):
		self._sock.close()

	def start(self):
		# self._threadRunning = True
		# self._readThread.start()
		err = self._bluez.hci_le_set_scan_enable(
		    self._sock.fileno(),
		    1,  # 1 - turn on;  0 - turn off
		    0, # 0-filtering disabled, 1-filter out duplicates
		    1000  # timeout
		)
		if err < 0:
			errnum = get_errno()
			raise Exception("{} {}".format(
			    errno.errorcode[errnum],
			    os.strerror(errnum)
			))

	def stop(self):
		# self._threadRunning = False
		# self._readThread.join()
		self._bluez.hci_le_set_scan_enable(
		    self._sock.fileno(),
		    0,  # 1 - turn on;  0 - turn off
		    0, # 0-filtering disabled, 1-filter out duplicates
		    1000  # timeout
		)


	def _setupProperties(self):
		"""
		Set up the radio properties we might need
		"""
		props = Properties.Properties()
		props.addr = self._getAddress()
		props.maxPacketLength = 72
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

	# def _backgroundRead(self):
	# 	while self._threadRunning:
	# 		client_sock = None
	# 		try:
	# 			#TODO: FIX THIS!!! THIS IS BLOCKING SO WE CAN NEVER END THIS SHIT
	# 			client_sock,address = self._sock.accept()
	# 			data = client_sock.recv(self.getProperties().maxPacketLength)
	# 			tmp = json.loads(data)
	# 			tmp['sentby'] = address[0] #want the address
	# 			pdb.set_trace()
	# 			self._readQ.put(tmp)
	# 		except bluetooth.btcommon.BluetoothError as e:
	# 			if 'timed out' not in e:
	# 				raise e
	# 		finally:
	# 			if client_sock is not None:
	# 				client_sock.close()
	# 	#
	# #

	def read(self):
		"""
		Read from radio and return json object

		Non blocking
		"""
		msg = {}
		try:
			data = self._sock.recv(1024)
			# print bluetooth address from LE Advert. packet
			msg = json.loads(''.join(x for x in data[20:-1]))
			addr = ':'.join("{0:02x}".format(ord(x)) for x in data[12:6:-1])
			msg['sentby'] = addr

		except bluetooth.btcommon.BluetoothError as e:
			if 'timed out' not in e:
				raise e

		return msg
	#

	def write(self, data):
		"""
		write json object to radio
		"""

		payload = ' '.join("{0:02X}".format(ord(x)) for x in json.dumps(data))
		length =  ''.join("{0:02X}".format(len(payload.split()) + 3))
		total = ''.join("{0:02X}".format(len(payload.split()) + 7))

		msgCmd = 'hcitool -i hci0 cmd 0x08 0x0008 ' + total + ' 02 01 1A ' + length + ' FF 4C 00 ' + payload
		onCmd = 'hcitool -i hci0 cmd 0x08 0x000a 01'
		offCmd = 'hcitool -i hci0 cmd 0x08 0x000a 00'
		try:
			subprocess.call(msgCmd, shell=True)
			subprocess.call(onCmd, shell=True)
			subprocess.call(offCmd, shell=True)
		except Exception as e:
			raise e
		#
	#
#