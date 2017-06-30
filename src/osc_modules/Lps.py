from .OscModule import OscModule
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
		self.name = self.get_name()
		self.server = server

	def routes(self):
		self.add_route('/set_node_number', self.osc_set_node_number)
		self.add_route('/{node_id}/set_position', self.osc_set_node_position)

	def osc_set_node_number(self, address, number):
		"""
		OSC listen:
			/set_node_number Int->number

		Set the number of LPS nodes
		"""
		self.server.lps_node_number = int(number)
		self._debug('New node number :', self.server.lps_node_number)

	def osc_set_node_position(self, address, x, y, z, **path_args):
		"""
		OSC listen:
			/{node_id}/set_position Float->x Float->y Float->z

		Set the position of the LPS with the ID {node_id}.
		WARNING : Needs a connected drone.
		"""

		node_id = int(path_args['node_id'])
		self._debug('setting node', node_id, 'position to:', x, y, z)
		if node_id < self.server.lps_node_number:
			drones = self.server.get_module('CRAZYFLIE').get_connected_drones()
			if len(drones) is 0:
				self._error('No drone connected')
				return
			else:
				anchor = LoPoAnchor(drones[0]['cf'])
				anchor.set_position(node_id, (x, y, z))

		else:
			self._error('Bad node_id ('+str(node_id)+'>='+self.server.lps_node_number+')')
