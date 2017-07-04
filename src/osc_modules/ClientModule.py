from .OscModule import OscModule

class ClientModule(OscModule):

	"""
	ClientModule class. Implements OSC routes related to OSC clients
	It allows to subscribe clients to packets this server sends
	"""

	@staticmethod
	def get_name():
		return 'CLIENT'

	def __init__(self, base_topic, server, debug=False):
		super(ClientModule, self).__init__(base_topic=base_topic, debug=debug)
		self.server = server

	def routes(self):
		self.add_route('/add', self.add_client)
		self.add_route('/remove', self.remove_client)

	def add_client(self, address, ip, port):
		"""
		OSC listen: /add
		:param str ip: the client ip to connect to 
		:param int port: the client port to connect to

		Adds a new client which will receive OSC messages from crazyflie-osc
		"""
		self._debug('adding client', ip+':'+port)
		if (ip, port) not in self.server.osc_clients:
			self.server.osc_clients[(ip, port)] = udp_client.SimpleUDPClient(ip, port)
			self._debug('success')
		else:
			self._debug('failure')

	def remove_client(self, address, ip, port):
		"""
		OSC listen: /remove
		:param str ip: the client ip to connect to 
		:param int port: the client port to connect to

		Removes an OSC client
		"""
		self._debug('removing client', ip+':'+port)
		if (ip, port) in self.server.osc_clients:
			del self.server.osc_clients[(ip, port)]
			self._debug('success')
		else:
			self._debug('failure')
