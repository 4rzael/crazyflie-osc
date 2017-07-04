def osc_requires(osc_module):
	def decorator(method):
		def wrapped(self, *args, **path_args):
			if self.server.get_module(osc_module) is None:
				self._error('required osc_module not found in server:', osc_module)
			else:
				return method(self, *args, **path_args)
		return wrapped
	return decorator


def _drone_exists(self, drone_id):
	return drone_id in self.server.drones

def drone_exists(method):
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
	@osc_requires('LPS')
	def wrapped(self, *args, **path_args):
		node_id = int(path_args['node_id'])
		if not _lps_node_exists(self, node_id):
			self._error('Bad node_id ('+str(node_id)+'>='+self.server.lps_node_number+')')
		else:
			return method(self, *args, **path_args)
	return wrapped


def _log_exists(self, drone_id, log_name):
	return ('logs' in self.server.drones[drone_id] and
			log_name in self.server.drones[drone_id]['logs'])

def log_exists(method):
	@osc_requires('LOG')
	@drone_exists
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		log_name = str(path_args['log_name'])
		if not _log_exists(self, drone_id, log_name):
			self._error('log name', log_name,' not found in drone', drone_id)
		else:
			return method(self, *args, **path_args)
	return wrapped


def one_drone_is_connected(method):
	@osc_requires('CRAZYFLIE')
	def wrapped(self, *args, **path_args):
		if len(self.server.get_module('CRAZYFLIE').get_connected_drones()) is 0:
			self._error('no drones connected')
		else:
			return method(self, *args, **path_args)
	return wrapped


def drone_connected(method):
	@drone_exists
	def wrapped(self, *args, **path_args):
		drone_id = int(path_args['drone_id'])
		if self.server.drones[drone_id]['connected'] is False:
			self._error('drone', drone_id, 'not connected')
		else:
			return method(self, *args, **path_args)
	return wrapped


def _param_exists(self, drone_id, param_group, param_name):
	return (param_group in self.drones[drone_id]['cf'].log.toc.toc and
			param_name in self.drones[drone_id]['cf'].log.toc.toc[param_group])

def param_exists(method):
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
	@osc_requires('CRAZYFLIE')
	def wrapped(self, *args, **path_args):
		drones = path_args['drones']
		if drones is '*':
			drones_ids = self.server.get_module('CRAZYFLIE').get_connected_drones()
		elif ';' not in drones:
			drones_ids = [drones]
		else:
			drones_ids = drones.split(';')

		for drone_id in drones_ids:
			path_args['drone_id'] = int(drone_id)
			try:
				method(self, *args, **path_args)
			except Exception as e:
				self._error(e)
	return wrapped


# def multi_drones_connected(method):
# 	def wrapped(self, *args, **path_args):
# 		drones_ids = path_args['drones_ids']

# 		filtered_drones_ids = [d for d in drones_ids if d in
# 			self.server.get_module('CRAZYFLIE').get_connected_drones()]

# 		for d in list(set(drones_ids) - set(filtered_drones_ids)):
# 			self._error('drone not found', d)

# 		path_args['drones_ids'] = filtered_drones_ids

# 		return method(self, *args, **path_args)
# 	return wrapped

# def multi_drones_param_exists(method):
# 	@multi_drones_connected
# 	def wrapped(self, *args, **path_args):
# 		drones_ids = path_args['drones_ids']
# 		param_group = str(path_args['param_group'])
# 		param_name = str(path_args['param_name'])

# 		filtered_drones_ids = [d for d in drones_ids if 
# 			_param_exists(self, d, param_group, param_name)]

# 		for d in list(set(drones_ids) - set(filtered_drones_ids)):
# 			self._error('param not found in drone', d,':',
# 				param_group+'.'+param_name)

# 		path_args['drones_ids'] = filtered_drones_ids

# 		return method(self, *args, **path_args)
# 	return wrapped
