from .OscModule import OscModule
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
from .osc_validators import *
import cflib
import threading

def set_interval(func, interval, *args, **kwargs):
    stopped = threading.Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args, **kwargs)
    threading.Thread(target=loop).start()
    return stopped.set

class CrazyflieModule(OscModule):

	"""
	CrazyflieModule class. Implements OSC routes related to the drones
	"""

	@staticmethod
	def get_name():
		return 'CRAZYFLIE'


	def __init__(self, server, base_topic, debug=False):
		super(CrazyflieModule, self).__init__(server=server, base_topic=base_topic, debug=debug)

		# Send goals to drones every 10ms
		@locks_drones
		def send_goal(self):
			for drone in self.server.drones.values():
				if drone['connected']:
					if drone['emergency']:
						drone['cf'].commander.send_stop_setpoint()
					elif drone['goal'] is not None:
						x, y, z, yaw = drone['goal']
						z = max(0, z) # do not send negative z waypoints
						(drone['cf']
						.commander
						.send_setpoint(y, x, yaw, int(z*1000)))
		self.stop_goal_timer = set_interval(send_goal, 25.0/1000.0, self)


	def routes(self):
		self.add_route('/{drone_id}/add', self.osc_add_drone)
		self.add_route('/{drone_id}/remove', self.osc_remove_drone)
		self.add_route('/{drone_id}/goal', self.osc_goal)
		self.add_route('/{drone_id}/goal/stop', self.osc_reset_goal)
		self.add_route('/{drones}/emergency', self.osc_emergency)
		self.add_route('/{drones}/lps/{nodes}/update_pos', self.osc_update_lps_pos)


	@locks_drones
	def stop(self):
		drones_ids = [k for k in self.server.drones.keys()]
		for did in drones_ids:
			self.osc_remove_drone('', drone_id=did)

		self.stop_goal_timer()



	@locks_drones
	def osc_add_drone(self, address, radio_url, **path_args):
		"""
		Adds a new drone with the ID {drone_id} and tries to connect on the URL radio_url.

		OSC listen: /{drone_id}/add
		
		:param radio_url: the radio url of the drone.
		:type radio_url: str.

		"""
		drone_id = int(path_args['drone_id'])
		self._debug('adding drone', drone_id, 'at url', radio_url)
		if drone_id not in self.server.drones:
			cf = Crazyflie()

			self.server.drones[drone_id] = {
				'radio_url': radio_url,
				'cf': cf,
				'connected': False,
				'goal': None,
				'emergency': False,
			}


			# connection callback
			def on_connection(uri):
				with self.server.drones as drones:
					self._debug('drone', drone_id, 'connected')
					drones[drone_id]['connected'] = True
					(drones[drone_id]['cf'].param.set_value('flightmode.posSet', '1'))

					# Send LPS nodes positions to the drone
					if self.server.get_module('LPS'):
						self.osc_update_lps_pos('',
							drones=drone_id,
							nodes='*')

					# init param module for this drone
					if self.server.get_module('PARAM'):
						self.server.get_module('PARAM').add_param_cb(drone_id)

					# Add default loggings for this drone
					if self.server.get_module('LOG'):
						self.server.get_module('LOG').add_default_loggers(drone_id)


			def on_connection_failed(uri, message):
				self._error('connection to drone', drone_id, 'failed:', message)

			def on_disconnection(uri):
				self._error('Drone', drone_id, 'disconnected')
				with self.server.drones as drones:
					if drone_id in drones:
						drones[drone_id]['connected'] = False

			# start the connection
			cf.connected.add_callback(on_connection)
			cf.connection_failed.add_callback(on_connection_failed)
			cf.disconnected.add_callback(on_disconnection)


		if not self.server.drones[drone_id]['connected']:
			self.server.drones[drone_id]['cf'].open_link(radio_url)
		else:
			self._error('drone', drone_id, 'already added and connected')


	@drone_connected
	def osc_goal(self, address, x, y, z, yaw, **path_args):
		"""
		Sends a 3D setpoint to the drone with ID {drone_id}.

		OSC listen: /{drone_id}/goal

		:param x: the X position.
		:type x: float.

		:param y: the Y position.
		:type y: float.

		:param z: the Z position.
		:type z: float.

		:param yaw: the yaw position.
		:type yaw: float.

		"""

		drone_id = int(path_args['drone_id'])
		self.server.drones[drone_id]['goal'] = (x, y, z, yaw)

	@drone_connected
	def osc_reset_goal(self, address, *args, **path_args):
		"""
		Stops sending goals to the drone with ID {drone_id}
		
		OSC listen: /{drone_id}/goal

		"""

		drone_id = int(path_args['drone_id'])
		self.server.drones[drone_id]['goal'] = None


	@drone_exists
	@locks_drones
	def osc_remove_drone(self, address, *args, **path_args):
		"""
		Disconnects and remove the drone with the given ID

		OSC listen: /{drone_id}/remove

		"""
		drone_id = int(path_args['drone_id'])
		if self.server.drones[drone_id]['connected']:
			# cut engines
			self.server.drones[drone_id]['cf'].commander.send_stop_setpoint()
			# disconnect
			self.server.drones[drone_id]['cf'].close_link()
		# remove
		del self.server.drones[drone_id]


	@multi_drones
	@drone_exists
	def osc_emergency(self, address, *args, **path_args):
		"""
		Sends an emergency signal to drones {drones}.
		An emergency stops engines and forbid the server to send setpoints to them

		OSC listen:
			/{drones}/emergency

		"""

		drone_id = int(path_args['drone_id'])
		self._debug('Emergency on drone', drone_id)

		self.server.drones[drone_id]['emergency'] = True


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
		Sends new lps nodes {nodes} positions to drones {drones} params

		OSC listen: /{drones}/lps/{nodes}/update_pos
		
		:param {drones}: drones ids separated by a ';'. * for all
		:type {drones}: str.
		:param {nodes}: nodes ids separated by a ';'. * for all
		:type {nodes}: str.

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
