from .OscModule import OscModule
from .osc_validators import log_exists, drone_connected, multi_drones
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
import cflib

class LogModule(OscModule):
	"""
	LogModule class. Implements OSC routes related to crazyflie logging
	"""

	@staticmethod
	def get_name():
		return 'LOG'


	def __init__(self, base_topic, server, debug=False):
		super(LogModule, self).__init__(base_topic=base_topic, debug=debug)
		self.server = server


	def routes(self):
		self.add_route('/{drones}/add', self.osc_add_log)
		self.add_route('/{drones}/{log_name}/add_variable', self.osc_log_add_variable)
		self.add_route('/{drones}/{log_name}/start', self.osc_log_start)
		self.add_route('/{drones}/send_toc', self.osc_send_toc)


	@multi_drones
	@drone_connected
	def osc_add_log(self, address,
					log_name, log_ms_period,
					**path_args):
		"""
		OSC listen: /{drones}/add_log

		:param str {drones}: drones ids separated by a ';'. * for all

		:param str log_name: the log parameter name
		:param int log_ms_period: the logging period in ms

		Adds a logger named log_name to drones {drones},
		which sends data every log_ms_period milliseconds
		"""

		drone_id = int(path_args['drone_id'])

		log = LogConfig(name=log_name, period_in_ms=log_ms_period)

		if 'logs' not in self.server.drones[drone_id]:
			self.server.drones[drone_id]['logs'] = {}

		self.server.drones[drone_id]['logs'][log_name] = log


	@multi_drones
	@log_exists
	def osc_log_add_variable(self, address,
							 variable_name, variable_type,
							 **path_args):
		"""
		OSC listen: /{drones}/{log_name}/add_variable

		:param str {drones}: drones ids separated by a ';'. * for all
		:param str {log_name}: the name of the log configuration

		:param str variable_name: the variable name to add
		:param int variable_type: the variable type

		Adds a variable {variable_name} of type {variable_type}
		to the log {log_name} of drones {drones}
		"""

		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])

		self.server.drones[drone_id]['logs'][log_name].add_variable(variable_name, variable_type)


	@multi_drones
	@log_exists
	def osc_log_start(self, address, *args,
					  **path_args):
		"""
		OSC listen: /{drones}/{log_name}/add_variable

		:param str {drones}: drones ids separated by a ';'. * for all
		:param str {log_name}: the name of the log configuration to start


		Starts the logger {log_name} of the drone {drones} 
		"""
		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])
		log = self.server.drones[drone_id]['logs'][log_name]

		self.server.drones[drone_id]['cf'].log.add_config(log)

		log.data_received_cb.add_callback(self._on_log_received)
		log.error_cb.add_callback(self._error)

		log.start()


	@multi_drones
	@drone_connected
	def osc_send_toc(self, address, *args,
					  **path_args):
		"""
		OSC listen: /{drones}send_toc

		:param str {drones}: drones ids separated by a ';'. * for all

		Sends log TOCs of drones {drones}
		"""

		drone_id = int(path_args['drone_id'])

		toc = self.server.drones[drone_id]['cf'].log.toc.toc
		toc = [{key: sorted([v for v in value])} for key, value in toc.items()]
		# toc = {key: [elem.name for elem in t.values()] for t in toc}
		print('TOC')
		for t in toc:
			print(t)


	def _on_log_received(self, *args, **kwargs):
		print(args, kwargs)