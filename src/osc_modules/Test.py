from .OscModule import OscModule

class TestModule(OscModule):
	@staticmethod
	def get_name():
		return 'TEST'

	def __init__(self, base_topic, debug=True):
		super(TestModule, self).__init__(base_topic=base_topic, debug=debug)
		self.name = self.get_name()

	def routes(self):
		self.add_route('/array', self.test_array)
		self.add_route('/vector', self.test_vector)

	def test_array(self, address, *values):
		self._debug('array received:', values)

	def test_vector(self, address, *vector):
		x, y, z = vector
		self._debug('vector received:', x, y, z)
