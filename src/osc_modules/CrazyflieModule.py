from .OscModule import OscModule
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
from .osc_validators import *
import cflib

class CrazyflieModule(OscModule):

	"""
	CrazyflieModule class. Implements OSC routes related to the drones
	"""

	@staticmethod
	def get_name():
		return 'CRAZYFLIE'

	def __init__(self, server, base_topic, debug=False):
		super(CrazyflieModule, self).__init__(server=server, base_topic=base_topic, debug=debug)


	def routes(self):
		self.add_route('/{drone_id}/add', self.osc_add_drone)
		self.add_route('/{drone_id}/remove', self.osc_remove_drone)
		self.add_route('/{drone_id}/goal', self.osc_goal)
		self.add_route('/{drones}/lps/{nodes}/update_pos', self.osc_update_lps_pos)


	def osc_add_drone(self, address, radio_url, **path_args):
		"""
		OSC listen: /{drone_id}/add
		:param str radio_url: the radio url of the drone

		Adds a new drone with the ID {drone_id} and tries to connect on the URL radio_url
		"""
		drone_id = int(path_args['drone_id'])
		self._debug('adding drone', drone_id, 'at url', radio_url)
		if drone_id not in self.server.drones:
			cf = Crazyflie()

			self.server.drones[drone_id] = {
				'radio_url': radio_url,
				'cf': cf,
				'connected': False
			}

			# connection callback
			def on_connection(uri):
				self._debug('drone', drone_id, 'connected')
				self.server.drones[drone_id]['connected'] = True
				(self.server.drones[drone_id]['cf']
				.param.set_value('flightmode.posSet', '1'))

				# Send LPS nodes positions to the drone
				if self.server.get_module('LPS'):
					self.osc_update_lps_pos('',
						drones=drone_id,
						nodes='*')

			def on_connection_failed(uri, message):
				self._error('connection to drone', drone_id, 'failed:', message)

			def on_disconnection(uri):
				self._error('Drone', drone_id, 'disconnected')
				self.server.drones[drone_id]['connected'] = False

			# start the connection
			cf.connected.add_callback(on_connection)
			cf.connection_failed.add_callback(on_connection_failed)
			cf.disconnected.add_callback(on_disconnection)

			# PARAM MODULE
			if self.server.get_module('PARAM'):
				self.server.get_module('PARAM').add_param_cb(drone_id)

		if not self.server.drones[drone_id]['connected']:
			self.server.drones[drone_id]['cf'].open_link(radio_url)
		else:
			self._error('drone', drone_id, 'already added and connected')


	@drone_connected
	def osc_goal(self, address, x, y, z, yaw, **path_args):
		"""
		OSC listen: /{drone_id}/goal
		:param float x: the X position
		:param float y: the Y position
		:param float z: the Z position
		:param float yaw: the yaw position

		Sends a 3D setpoint to the drone with ID {drone_id}
		"""
		drone_id = int(path_args['drone_id'])
		(self.server.drones[drone_id]['cf']
		.commander.send_setpoint(y, x, yaw, int(z*1000)))


	@drone_exists
	def osc_remove_drone(self, address, **path_args):
		"""
		OSC listen:
			/{drone_id}/remove

			Disconnects and remove the drone with the given ID
		"""
		drone_id = int(path_args['drone_id'])
		if self.server.drones[drone_id]['connected']:
			self.server.drones[drone_id]['cf'].close_link()
		del self.server.drones[drone_id]


	def get_connected_drones(self):
		return [drone for drone in self.server.drones.values() if drone['connected']]


	@osc_requires('LPS')
	@osc_requires('PARAM')
	@multi_drones
	@multi_nodes
	@drone_connected
	@lps_node_has_position
	def osc_update_lps_pos(self, address, *args,
		**path_args):
		"""
		OSC listen: /{drones}/lps/{nodes}/update_pos
		
		:param str {drones}: drones ids separated by a ';'. * for all
		:param str {nodes}: nodes ids separated by a ';'. * for all

		Sends new lps nodes {nodes} positions to drones {drones} params
		"""

		drone_id = path_args['drone_id']
		node_id = path_args['node_id']

		self._debug('Updating lps node', node_id, 'position in drone', drone_id)

		param_module = self.server.get_module('PARAM')
		param_module.osc_set_param(None,
			param_group='anchorpos', param_name='anchor'+str(node_id)+'x',
			value=self.server.lps_positions[node_id][0], **path_args)
		param_module.osc_set_param(None,
			param_group='anchorpos', param_name='anchor'+str(node_id)+'y',
			value=self.server.lps_positions[node_id][1], **path_args)
		param_module.osc_set_param(None,
			param_group='anchorpos', param_name='anchor'+str(node_id)+'z',
			value=self.server.lps_positions[node_id][2], **path_args)
