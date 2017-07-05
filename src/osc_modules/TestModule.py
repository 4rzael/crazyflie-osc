from .OscModule import OscModule
from .osc_validators import *

class TestModule(OscModule):
	@staticmethod
	def get_name():
		return 'TEST'

	def __init__(self, server, base_topic, debug=True):
		super(TestModule, self).__init__(server=server, base_topic=base_topic, debug=debug)
		self.name = self.get_name()

	def routes(self):
		self.add_route('/vector', self.test_vector)
		self.add_route('/ping', self.ping)
		self.add_route('/{call_id}/generic_call', self.generic_call)
		self.add_route('/{call_id}/generic_call/{not_generic}', self.not_generic_call)
		self.add_route('/{call_id}/generic_call/special', self.special_call)

	def test_vector(self, address, *vector):
		x, y, z = vector
		self._debug('vector received:', x, y, z)

	@osc_requires('CLIENT')
	def ping(self, address, data):
		self._debug('ping', data)
		self._send('/pong', data)

	def generic_call(self, address, *args, **path_args):
		self._debug('generic', path_args)

	def not_generic_call(self, address, *args, **path_args):
		self._debug('not_generic', path_args)

	def special_call(self, address, *args, **path_args):
		self._debug('special', path_args)