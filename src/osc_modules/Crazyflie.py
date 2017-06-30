from .OscModule import OscModule
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
import cflib

class CrazyflieModule(OscModule):

	"""
	CrazyflieModule class. Implements OSC routes related to the drones
	"""

	@staticmethod
	def get_name():
		return 'CRAZYFLIE'

	def __init__(self, base_topic, server, debug=False):
		super(CrazyflieModule, self).__init__(base_topic=base_topic, debug=debug)
		self.name = self.get_name()
		self.server = server

	def routes(self):
		self.add_route('/{drone_id}/add', self.osc_add_drone)
		self.add_route('/{drone_id}/remode', self.osc_remove_drone)
		self.add_route('/{drone_id}/goal', self.osc_goal)

	def osc_add_drone(self, address, radio_url, **path_args):
		"""
		OSC listen:
			/{drone_id}/add String->RADIO_URL

		Adds a new drone with the ID {drone_id} and tries to connect on the URL RADIO_URL
		"""
		drone_id = path_args['drone_id']
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

			def on_connection_failed(uri, message):
				self._error('connection to drone', drone_id, 'failed:', message)

			def on_disconnection(uri):
				self._error('Drone', drone_id, 'disconnected')
				self.server.drones[drone_id]['connected'] = False

			# start the connection
			cf.connected.add_callback(on_connection)
			cf.connection_failed.add_callback(on_connection_failed)
			cf.disconnected.add_callback(on_disconnection)

		if not self.server.drones[drone_id]['connected']:
			self.server.drones[drone_id]['cf'].open_link(radio_url)
		else:
			self._error('drone', drone_id, 'already added and connected')

	def osc_goal(self, address, x, y, z, yaw, **path_args):
		"""
		OSC listen:
			/{drone_id}/goal Float->x Float->y Float->z Float->yaw

			Sends a 3D setpoint to the drone with ID {drone_id}
		"""
		drone_id = path_args['drone_id']
		if drone_id in self.server.drones:
			(self.server.drones[drone_id]['cf']
			.commander.send_setpoint(y, x, yaw, int(z*1000)))

	def osc_remove_drone(self, address, **path_args):
		"""
		OSC listen:
			/{drone_id}/remove

			Disconnects and remove the drone with the given ID
		"""
		drone_id = path_args['drone_id']	
		if drone_id in self.server.drones:
			if self.server.drones[drone_id]['connected']:
				self.server.drones[drone_id]['cf'].close_link()
			del self.server.drones[drone_id]
		else:
			self._error('cannot delete drone', drone_id, ': it does not exist')

	def get_connected_drones(self):
		return [drone for drone in self.server.drones.values() if drone['connected']]