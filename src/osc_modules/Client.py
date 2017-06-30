from .OscModule import OscModule

class ClientModule(OscModule):

	@staticmethod
	def get_name():
		return 'CLIENT'

	def __init__(self, base_topic, server, debug=False):
		super(ClientModule, self).__init__(base_topic=base_topic, debug=debug)
		self.name = self.get_name()
		self.server = server

	def routes(self):
		self.add_route('/add', self.add_client)
		self.add_route('/remove', self.remove_client)

	def add_client(self, address, host, port):
		self._debug('adding client', host+':'+port)
		if (host, port) not in self.server.osc_clients:
			self.server.osc_clients[(host, port)] = udp_client.SimpleUDPClient(host, port)
			self._debug('success')
		else:
			self._debug('failure')

	def remove_client(self, address, host, port):
		self._debug('removing client', host+':'+port)
		if (host, port) in self.server.osc_clients:
			del self.server.osc_clients[(host, port)]
			self._debug('success')
		else:
			self._debug('failure')
