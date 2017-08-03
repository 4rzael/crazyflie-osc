from .OscModule import OscModule
from .osc_validators import *
from .CrazyflieModule import set_interval

class TestModule(OscModule):
	@staticmethod
	def get_name():
		return 'TEST'

	def __init__(self, server, base_topic, debug=True):
		super(TestModule, self).__init__(server=server, base_topic=base_topic, debug=debug)
		self.name = self.get_name()

		self.tick = 0
		def send_tick():
			self.tick += 1
			self._debug(self.tick)
			self._send('/tick', self.tick)
		self.stop_tick_timer = set_interval(send_tick, 0.1)

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

	def stop(self):
		self.stop_tick_timer()
