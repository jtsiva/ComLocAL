

class CommmandPacket(object):
	"""
	Packet used to send and receive data as well as control
	aspects of the ComLocAL module behavior. Similar to how
	AT commands from ZigBee can be wrapped in packets to operate
	locally or remotely
	"""
	def __init__(self):
		"""
		type: 0 - addressed data packet
		      1 - geo-addressed data packet (r_start, r_end) [in meters]
		      2 - addressed command packet (data = command + params)
		      3 - geo-addressed command packet (data = command + params)
		"""
		self._type = 0
		self._addr = ''
		self._data = []
#