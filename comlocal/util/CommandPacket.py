"""
Notes on addressing:
using an address means using a UAV_ID which takes the form of:
	[organizational ID]:[App ID]:[Serial #]
	[4 bytes]:[2 bytes]:[2 bytes]
	[2]:[1]:[1]?

	ADDRESS ALL: 0:0:0 (useful for BSMs)

geo-addressing refers to indicating either a range of interest
for the packet or a location, and it look like:
	[start radius]:[end radius]
	or
	[x coor/longitude]:[y coor/latitude]:[radius from point]

	??? SHOULD WE USE RELATIVE LOCATIONS ???

	[2 bytes]:[2 bytes]:[2 bytes]---\
	[1]:[1]:[1]----------------------- probably need relative loc
	all of these are integers
"""

class CommmandPacket(object):
	"""
	Packet used to send and receive data as well as control
	aspects of the ComLocAL module behavior. Similar to how
	AT commands from ZigBee can be wrapped in packets to operate
	locally or remotely
	"""
	def __init__(self):
		"""
		type: 0x00 - addressed data packet
		      0x01 - geo-addressed data packet (r_start, r_end) [in meters]
		      0x02 - addressed command packet (data = command + params)
		      0x03 - geo-addressed command packet (data = command + params)

		      0x8F |= type => response (primarily for command packets)
		"""
		self._type = 0
		self._addr = ''
		self._data = []
	#
#