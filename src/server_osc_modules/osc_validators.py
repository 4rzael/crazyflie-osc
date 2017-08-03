import traceback
from functools import wraps

def osc_requires(osc_module):
	def decorator(method):
		@wraps(method)
		def wrapped(self, *args, **kwargs):
			if self.server.get_module(osc_module) is None:
				self._error('required osc_module not found in server:', osc_module)
			else:
				return method(self, *args, **kwargs)
		return wrapped
	return decorator


def _drone_exists(self, drone_id):
	return drone_id in self.server.drones

def drone_exists(method):
	@wraps(method)
	@osc_requires('CRAZYFLIE')
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		if not _drone_exists(self, drone_id):
			self._error('drone not found :', drone_id)
		else:
			return method(self, *args, **path_args)
	return wrapped


def _lps_node_exists(self, node_id):
	return node_id < self.server.lps_node_number

def lps_node_exists(method):
	@wraps(method)
	@osc_requires('LPS')
	def wrapped(self, *args, **path_args):
		node_id = int(path_args['node_id'])
		if not _lps_node_exists(self, node_id):
			self._error('Bad node_id ('+str(node_id)+'>='+str(self.server.lps_node_number)+')')
		else:
			return method(self, *args, **path_args)
	return wrapped


def lps_node_has_position(method):
	@wraps(method)
	@lps_node_exists
	def wrapped(self, *args, **path_args):
		node_id = int(path_args['node_id'])
		if self.server.lps_positions[node_id] is None:
			self._error('lps node', node_id, 'position not set')
		else:
			return method(self, *args, **path_args)
	return wrapped


def _log_exists(self, drone_id, log_name):
	return ('logs' in self.server.drones[drone_id] and
			log_name in self.server.drones[drone_id]['logs'])

def log_exists(method):
	@wraps(method)
	@osc_requires('LOG')
	@drone_exists
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])
		if not _log_exists(self, drone_id, log_name):
			self._error('log name', log_name,'not found in drone', drone_id)
		else:
			return method(self, *args, **path_args)
	return wrapped


def log_not_started(method):
	@wraps(method)
	@osc_requires('LOG')
	@log_exists
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])
		if self.server.drones[drone_id]['logs'][log_name].started:
			self._error('log', log_name,'in drone', drone_id, 'already started')
		else:
			return method(self, *args, **path_args)
	return wrapped


def one_drone_is_connected(method):
	@wraps(method)
	@osc_requires('CRAZYFLIE')
	def wrapped(self, *args, **path_args):
		if len(self.server.get_module('CRAZYFLIE').get_connected_drones()) is 0:
			self._error('no drones connected')
		else:
			return method(self, *args, **path_args)
	return wrapped


def drone_connected(method):
	@wraps(method)
	@drone_exists
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		if self.server.drones[drone_id]['connected'] is False:
			self._error('drone', drone_id, 'not connected')
		else:
			return method(self, *args, **path_args)
	return wrapped

def _param_exists(self, drone_id, param_group, param_name):
	return (param_group in self.server.drones[drone_id]['cf'].param.toc.toc and
			param_name in self.server.drones[drone_id]['cf'].param.toc.toc[param_group])

def param_exists(method):
	@wraps(method)
	@osc_requires('PARAM')
	@drone_connected
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		param_group = str(path_args['param_group'])
		param_name = str(path_args['param_name'])
		if not _param_exists(self, drone_id, param_group, param_name):
			self._error('param', param_group+'.'+param_name, 'not found in drone', drone_id)
		else:
			return method(self, *args, **path_args)
	return wrapped



## MULTI DRONES OSC VALIDATORS
def multi_drones(method):
	@wraps(method)
	@osc_requires('CRAZYFLIE')
	def wrapped(self, *args, **path_args):
		drones = str(path_args['drones'])
		if drones is '*':
			drones_ids = self.server.drones.keys()
		elif ';' in drones:
			drones_ids = drones.split(';')
		else:
			drones_ids = [drones]

		for drone_id in drones_ids:
			path_args['drone_id'] = int(drone_id)
			try:
				return method(self, *args, **path_args)
			except Exception as e:
				self._error('Exception catched :', traceback.format_exc())
	return wrapped


## MULTI LPS NODE OSC VALIDATORS

def multi_nodes(method):
	@wraps(method)
	@osc_requires('LPS')
	def wrapped(self, *args, **path_args):
		nodes = str(path_args['nodes'])
		if nodes is '*':
			nodes_ids = range(0, self.server.lps_node_number)
		elif ';' in nodes:
			nodes_ids = nodes.split(';')
		else:
			nodes_ids = [nodes]

		for node_id in nodes_ids:
			path_args['node_id'] = int(node_id)
			try:
				method(self, *args, **path_args)
			except Exception as e:
				self._error('Exception catched :', traceback.format_exc())
	return wrapped
