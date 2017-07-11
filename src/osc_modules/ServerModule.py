from .OscModule import OscModule

class ServerModule(OscModule):

	"""
	ServerModule class. Implements OSC routes related to this OSC server internal mechanics
	"""

	@staticmethod
	def get_name():
		return 'SERVER'

	def __init__(self, server, base_topic, debug=False):
		super(ServerModule, self).__init__(server=server, base_topic=base_topic, debug=debug)

	def routes(self):
		self.add_route('/restart', self.osc_restart)

	def osc_restart(self, address, *args):
		"""
		Restarts the server

		OSC listen: /restart
		"""

		self.server.stop()
