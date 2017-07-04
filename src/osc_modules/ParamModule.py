from .OscModule import OscModule
from .osc_validators import param_exists, drone_connected, multi_drones
from cflib.crazyflie import Crazyflie
import cflib

class ParamModule(OscModule):
	"""
	ParamModule class. Implements OSC routes related to crazyflie logging
	"""

	@staticmethod
	def get_name():
		return 'PARAM'

	def __init__(self, server, base_topic, debug=False):
		super(ParamModule, self).__init__(server=server, base_topic=base_topic, debug=debug)

	def routes(self):
		self.add_route('/{drones}/{param_group}/{param_name}/set', self.osc_set_param)
		self.add_route('/{drones}/send_toc', self.osc_send_toc)


	@multi_drones
	@param_exists
	@drone_connected
	def osc_set_param(self, address, value,
					**path_args):
		"""
		OSC listen: /{drones}/{param_group}/{param_name}/set

		:param str {drones}: drones ids separated by a ';'. * for all
		:param str {param_group}: group of the param to set
		:param str {param_name}: name of the param to set

		:param str value: the value to set to the param

		Sets the param named {param_group}.{param_name} in drones {drones}
		"""

		drone_id = int(int(path_args['drone_id']))
		param_group = str(path_args['param_group'])
		param_name = str(path_args['param_name'])

		self._debug('setting param', param_group+'.'+param_name,
			'in drone', drone_id, 'to value', str(value))

		self.server.drones[drone_id]['cf'].\
		param.set_value(param_group+'.'+param_name, str(value))

	@multi_drones
	@drone_connected
	def osc_send_toc(self, address, *args,
					  **path_args):
		"""
		OSC listen: /{drones}send_toc

		:param str {drones}: drones ids separated by a ';'. * for all

		Sends param TOCs of drones {drones}
		"""

		drone_id = int(int(path_args['drone_id']))

		toc = self.server.drones[drone_id]['cf'].param.toc.toc
		toc = [{key: sorted([v for v in value])} for key, value in toc.items()]
		# toc = {key: [elem.name for elem in t.values()] for t in toc}
		print('TOC')
		for t in toc:
			print(t)


	def add_param_cb(self, drone_id):
		if drone_id in self.server.drones and self.server.drones[drone_id]['connected']:
			for group in self.server.drones[drone_id]['cf'].param.toc.toc:
				self.server.drones[drone_id]['cf']\
				.param.add_update_callback(group=group, name=None, cb=self._on_param_update)


	def _on_param_update(self, *args, **kwargs):
		print(args, kwargs)