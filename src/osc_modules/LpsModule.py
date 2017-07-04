from .OscModule import OscModule
from .osc_validators import lps_node_exists, one_drone_is_connected, multi_nodes
from lpslib.lopoanchor import LoPoAnchor

class LpsModule(OscModule):
	"""
	LpsModule class. Implements OSC routes related to LPS nodes
	"""

	@staticmethod
	def get_name():
		return 'LPS'


	def __init__(self, server, base_topic, debug=False):
		super(LpsModule, self).__init__(server=server, base_topic=base_topic, debug=debug)


	def routes(self):
		self.add_route('/set_node_number', self.osc_set_node_number)
		self.add_route('/{node_id}/set_position', self.osc_set_node_position)
		self.add_route('/{nodes}/reboot', self.osc_reboot)

	def osc_set_node_number(self, address, number):
		"""
		OSC listen: /set_node_number
		:param int number: the number of LPS nodes in the system

		Set the number of LPS nodes
		"""

		number = int(number)

		# extends or shrink the position savings on the server
		if number <= self.server.lps_node_number:
			self.server.lps_positions = self.server.lps_positions[:number]
		else:
			self.server.lps_positions = self.server.lps_positions + (
				[None] * number - self.server.lps_node_number)

		self.server.lps_node_number = number
		self._debug('New node number :', self.server.lps_node_number)


	@one_drone_is_connected
	@lps_node_exists
	def osc_set_node_position(self, address, x, y, z, **path_args):
		"""
		OSC listen: /{node_id}/set_position
		:param int {node_id}: the id of the node to change (starting at 0)

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

		self.server.lps_positions[node_id] = (x, y, z)

		crazyflie_module = self.server.get_module('CRAZYFLIE')
		crazyflie_module.osc_update_lps_pos('',
			drones='*',
			nodes=node_id)


	@multi_nodes
	@one_drone_is_connected
	@lps_node_exists
	def osc_reboot(self, address, reboot_bootloader=False, **path_args):
		"""
		OSC listen: /{nodes}/reboot
		:param str {nodes}: nodes ids separated by a ';'. * for all

		:param bool reboot_bootloader: default to False.\
			Either it should be rebooted in bootloader mode instead of firmware
		:param float y: the Y position
		:param float z: the Z position

		Set the position of LPS nodes with IDs {nodes}.
		WARNING : Needs a connected drone.
		"""

		node_id = int(path_args['node_id'])
		self._debug('rebooting node', node_id)
		drones = self.server.get_module('CRAZYFLIE').get_connected_drones()
		anchor = LoPoAnchor(drones[0]['cf'])
		anchor.reboot(node_id, LoPoAnchor.REBOOT_TO_BOOTLOADER if reboot_bootloader else LoPoAnchor.REBOOT_TO_FIRMWARE)
