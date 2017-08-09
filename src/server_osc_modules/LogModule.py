from .OscModule import OscModule
from .osc_validators import *
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
import cflib
import json

class Logger(object):

	def __init__(self, log):
		self.log = log
		self.variables = []
		self.started = False

	def add_variable(self, var, var_type):
		self.variables.append(var)
		self.log.add_variable(var, var_type)

	def add_data_received_callback(self, callback):
		self.log.data_received_cb.add_callback(callback)

	def add_error_callback(self, callback):
		self.log.error_cb.add_callback(callback)

	def start(self):
		self.started = True
		self.log.start()


class LogModule(OscModule):
	"""
	LogModule class. Implements OSC routes related to crazyflie logging.

	OSC publish :

	/{drone_id}/toc -> json

	/{drone_id}/toc/{toc_variable} -> str[]

	/{drone_id}/{log_name} -> value[]

	/{drone_id}/{log_name}/{variable_name} -> value

	Default OSC publish :

	/{drone_id}/position

	/{drone_id}/battery

	TODO /{drone_id}/goal

	"""

	@staticmethod
	def get_name():
		return 'LOG'


	def __init__(self, server, base_topic, debug=False):
		super(LogModule, self).__init__(server=server, base_topic=base_topic, debug=debug)


	def routes(self):
		self.add_route('/{drones}/add', self.osc_add_log)
		self.add_route('/{drones}/{log_name}/add_variable', self.osc_log_add_variable)
		self.add_route('/{drones}/{log_name}/start', self.osc_log_start)
		self.add_route('/{drones}/send_toc', self.osc_send_toc)
		self.add_route('/{drones}/send_toc/{toc_variable}', self.osc_send_toc_variable)


	@multi_drones
	@drone_connected
	def osc_add_log(self, address,
					log_name, log_ms_period,
					**path_args):
		""" Adds a logger named log_name to drones {drones}, which sends data every log_ms_period milliseconds.

		OSC listen: /{drones}/add

		:param {drones}: drones ids separated by a ';'. * for all
		:type {drones}: str.

		:param log_name: the log parameter name.
		:type log_name: str.

		:param log_ms_period: the logging period in ms.
		:type log_ms_period: int.
		"""

		drone_id = int(path_args['drone_id'])
		log_name = str(log_name)
		log_ms_period = int(log_ms_period)

		if 'logs' not in self.server.drones[drone_id]:
			self.server.drones[drone_id]['logs'] = {}

		if log_name in self.server.drones[drone_id]['logs']:
			self._error('log', log_name, 'already exists')
			return

		log = LogConfig(name=log_name, period_in_ms=log_ms_period)

		self.server.drones[drone_id]['logs'][log_name] = Logger(log)
		self._debug('adding new log:', log_name,'period:', log_ms_period)


	@multi_drones
	@log_exists
	@log_not_started
	def osc_log_add_variable(self, address,
							 variable_name, variable_type,
							 **path_args):
		""" Adds a variable {variable_name} of type {variable_type}
		to the log {log_name} of drones {drones}.

		OSC listen: /{drones}/{log_name}/add_variable

		:param {drones}: drones ids separated by a ';'. * for all.
		:type {drones}: str.
		:param {log_name}: the name of the log configuration.
		:type {log_name}: str.

		:param variable_name: the variable name to add.
		:type variable_name: str.
		:param variable_type: the variable type.
		:type variable_type: int.

		"""

		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])

		self.server.drones[drone_id]['logs'][log_name].add_variable(variable_name, variable_type)
		self._debug('adding', variable_name, 'to', log_name)


	@multi_drones
	@log_exists
	@log_not_started
	def osc_log_start(self, address, *args,
					  **path_args):
		""" Starts the logger {log_name} of the drone {drones}.

		OSC listen: /{drones}/{log_name}/start

		:param {drones}: drones ids separated by a ';'. * for all.
		:type {drones}: str.
		:param {log_name}: the name of the log configuration to start.
		:type {log_name}: str.

		"""
		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])
		logger = self.server.drones[drone_id]['logs'][log_name]

		self.server.drones[drone_id]['cf'].log.add_config(logger.log)

		logger.add_data_received_callback(
			self._on_log_received(drone_id, log_name))
		logger.add_error_callback(self._error)

		logger.start()


	def _get_toc(self, drone_id):
		toc = self.server.drones[drone_id]['cf'].log.toc.toc.items()
		toc = {key: sorted([v for v in value]) for key, value in toc}
		return toc


	@multi_drones
	@drone_connected
	def osc_send_toc_variable(self, address, *args,
					  **path_args):
		""" Sends a log TOC variable {toc_variable} from drones {drones} as an array.

		OSC listen: /{drones}/send_toc/{toc_variable}

		:param {drones}: drones ids separated by a ';'. * for all.
		:type {drones}: str.
		:param {toc_variable}: the toc variable name.
		:type {toc_variable}: str.
		"""

		drone_id = int(path_args['drone_id'])
		toc_variable = str(path_args['toc_variable'])

		toc = self._get_toc(drone_id)
		if toc_variable in toc:
			self._send('/'.join([drone_id, toc_variable]), toc[toc_variable])


	@multi_drones
	@drone_connected
	def osc_send_toc(self, address, *args,
					  **path_args):
		""" Sends log TOCs of drones {drones} as JSON.

		OSC listen: /{drones}/send_toc.

		:param {drones}: drones ids separated by a ';'. * for all.
		:type {drones}: str.

		"""

		print(address)

		drone_id = int(path_args['drone_id'])

		toc = self._get_toc(drone_id)

		self._send('/'+str(drone_id)+'/toc', json.dumps(toc))

	def _on_log_received(self, drone_id, log_name):
		log_name = str(log_name)
		drone_id = int(drone_id)

		logger = self.server.drones[drone_id]['logs'][log_name]
		def callback(log_id, log_content, log_object):
			# send each variable on /{drone_id}/{log_name}/{variable}
			for var, value in log_content.items():
				self._send('/'.join([str(drone_id), log_name, var]),
					value)
			# send a json on /{drone_id}/{log_name}

#			self._debug('Log', log_name, 'received :', log_content)

			self._send('/'.join([str(drone_id), log_name]),
				[log_content[var] for var in logger.variables])

		return callback

	def add_default_loggers(self, drone_id):
		drone_id = int(drone_id)

		# position -> x y z
		self.osc_add_log('', 'position', 200,
			drones=drone_id)
		self.osc_log_add_variable('', 'kalman.stateX', 'float',
			drones=drone_id,
			log_name='position')
		self.osc_log_add_variable('', 'kalman.stateY', 'float',
			drones=drone_id,
			log_name='position')
		self.osc_log_add_variable('', 'kalman.stateZ', 'float',
			drones=drone_id,
			log_name='position')
		self.osc_log_start('',
			drones=drone_id,
			log_name='position')
		# battery voltage
		self.osc_add_log('', 'battery', 1000,
			drones=drone_id)
		self.osc_log_add_variable('', 'pm.vbat', 'float',
			drones=drone_id,
			log_name='battery')
		self.osc_log_start('',
			drones=drone_id,
			log_name='battery')

