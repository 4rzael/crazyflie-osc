from .OscModule import OscModule
from .osc_validators import lps_node_exists, one_drone_is_connected
from lpslib.lopoanchor import LoPoAnchor

class LpsModule(OscModule):
	"""
	LpsModule class. Implements OSC routes related to LPS nodes
	"""

	@staticmethod
	def get_name():
		return 'LPS'


	def __init__(self, base_topic, server, debug=False):
		super(LpsModule, self).__init__(base_topic=base_topic, debug=debug)
		self.server = server


	def routes(self):
		self.add_route('/set_node_number', self.osc_set_node_number)
		self.add_route('/{node_id}/set_position', self.osc_set_node_position)
		self.add_route('/{node_id}/reboot', self.osc_reboot)


	def osc_set_node_number(self, address, number):
		"""
		OSC listen: /set_node_number
		:param int number: the number of LPS nodes in the system

		Set the number of LPS nodes
		"""
		self.server.lps_node_number = int(number)
		self._debug('New node number :', self.server.lps_node_number)


	@one_drone_is_connected
	@lps_node_exists
	def osc_set_node_position(self, address, x, y, z, **path_args):
		"""
		OSC listen: /{node_id}/set_position
		:param float x: the X position
		:param float y: the Y position
		:param float z: the Z position

		Set the position of the LPS with the ID {node_id}.
		WARNING : Needs a connected drone.
		"""

		node_id = int(path_args['node_id'])
		self._debug('setting node', node_id, 'position to:', x, y, z)

		drones = self.server.get_module('CRAZYFLIE').get_connected_drones()

		anchor = LoPoAnchor(drones[0]['cf'])
		anchor.set_position(node_id, (x, y, z))

	@one_drone_is_connected
	@lps_node_exists
	def osc_reboot(self, address, reboot_bootloader=False, **path_args):
		"""
		OSC listen: /{node_id}/reboot
		:param bool reboot_bootloader: default to False.\
			Either it should be rebooted in bootloader mode instead of firmware
		:param float y: the Y position
		:param float z: the Z position

		Set the position of the LPS with the ID {node_id}.
		WARNING : Needs a connected drone.
		"""

		node_id = int(path_args['node_id'])
		self._debug('rebooting node', node_id)
		drones = self.server.get_module('CRAZYFLIE').get_connected_drones()
		anchor = LoPoAnchor(drones[0]['cf'])
		anchor.reboot(node_id, LoPoAnchor.REBOOT_TO_BOOTLOADER if reboot_bootloader else LoPoAnchor.REBOOT_TO_FIRMWARE)

