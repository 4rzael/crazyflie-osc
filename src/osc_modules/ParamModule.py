from .OscModule import OscModule
from .osc_validators import *
from cflib.crazyflie import Crazyflie
import cflib
import json

class ParamModule(OscModule):
	"""ParamModule class. Implements OSC routes related to crazyflie params

	OSC publish :
	/{drone_id}/toc -> json
	/{drone_id}/toc/{toc_variable} -> str[]
	/{drone_id}/{param_group}/{param_name} -> value

	"""

	@staticmethod
	def get_name():
		return 'PARAM'

	def __init__(self, server, base_topic, debug=False):
		super(ParamModule, self).__init__(server=server, base_topic=base_topic, debug=debug)

	def routes(self):
		self.add_route('/{drones}/{param_group}/{param_name}/set', self.osc_set_param)
		self.add_route('/{drones}/send_toc', self.osc_send_toc)
		self.add_route('/{drones}/send_toc/{toc_variable}', self.osc_send_toc_variable)
		self.add_route('/{drones}/get_all_values', self.osc_get_all_values)


	@multi_drones
	@param_exists
	@drone_connected
	def osc_set_param(self, address, value,
					**path_args):
		"""Sets the param named {param_group}.{param_name} in drones {drones}.

		OSC listen: /{drones}/{param_group}/{param_name}/set

		:param {drones}: drones ids separated by a ';'. * for all
		:type {drones}: str.

		:param {param_group}: group of the param to set.
		:type {param_group}: str.
		:param {param_name}: name of the param to set.
		:type {param_name}: str.

		:param value: the value to set to the param
		:type value: str.
		"""

		drone_id = int(int(path_args['drone_id']))
		param_group = str(path_args['param_group'])
		param_name = str(path_args['param_name'])

		self._debug('setting param', param_group+'.'+param_name,
			'in drone', drone_id, 'to value', str(value))

		self.server.drones[drone_id]['cf'].\
		param.set_value(param_group+'.'+param_name, str(value))


	@locks_drones
	def _get_toc(self, drone_id):
		toc = self.server.drones[drone_id]['cf'].param.toc.toc.items()
		toc = {key: sorted([v for v in value]) for key, value in toc}
		return toc


	@multi_drones
	@drone_connected
	def osc_send_toc_variable(self, address, *args,
					  **path_args):
		"""Sends a param TOC variable {toc_variable} from drones {drones} as an array.

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
			self._send('/'+str(drone_id)+'/toc/'+toc_variable, toc[toc_variable])


	@multi_drones
	@drone_connected
	def osc_send_toc(self, address, *args,
					  **path_args):
		"""Sends param TOCs of drones {drones} as JSON.

		OSC listen: /{drones}/send_toc

		:param {drones}: drones ids separated by a ';'. * for all.
		:type {drones}: str.

		"""

		print(address)

		drone_id = int(path_args['drone_id'])

		toc = self._get_toc(drone_id)

		self._send('/'+str(drone_id)+'/toc', json.dumps(toc))


	@multi_drones
	@drone_connected
	@locks_drones
	def osc_get_all_values(self, address, *args, **path_args):
		"""Sends all param values of drones {drones}

		OSC listen: /{drones}/get_all_values

		:param {drones}: drones ids separated by a ';'. * for all.
		:type {drones}: str.

		"""
		drone_id = int(path_args['drone_id'])

		self.server.drones[drone_id]['cf'].param.request_update_of_all_params()


	@locks_drones
	def add_param_cb(self, drone_id):
		if drone_id in self.server.drones and self.server.drones[drone_id]['connected']:
			for group in self.server.drones[drone_id]['cf'].param.toc.toc:
				self.server.drones[drone_id]['cf']\
				.param.add_update_callback(group=group, name=None,
					cb=self._on_param_update(drone_id))


	def _on_param_update(self, drone_id):
		drone_id = str(drone_id)
		def callback(param, value):
			param_group, param_name = param.split('.')
			self._send('/'.join([drone_id, param_group, param_name]),
				value)
		return callback
