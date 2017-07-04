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

	def test_vector(self, address, *vector):
		x, y, z = vector
		self._debug('vector received:', x, y, z)

	@osc_requires('CLIENT')
	def ping(self, address, data):
		self._debug('ping', data)
		self._send('/pong', data)
