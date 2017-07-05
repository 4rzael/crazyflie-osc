from .OscModule import OscModule
from pythonosc import udp_client

class ClientModule(OscModule):

	"""
	ClientModule class. Implements OSC routes related to OSC clients
	It allows to subscribe clients to packets this server sends
	"""

	@staticmethod
	def get_name():
		return 'CLIENT'

	def __init__(self, server, base_topic, debug=False):
		super(ClientModule, self).__init__(server=server, base_topic=base_topic, debug=debug)

	def routes(self):
		self.add_route('/add', self.osc_add_client)
		self.add_route('/remove', self.osc_remove_client)

	def osc_add_client(self, address, ip, port):
		"""
		Adds a new client which will receive OSC messages from crazyflie-osc.

		OSC listen: /add

		:param str ip: the client ip to connect to.
		:type ip: str.
		:param int port: the client port to connect to.
		:type port: int.

		"""

		ip = str(ip)
		port = int(port)

		self._debug('adding client', ip+':'+str(port))
		if (ip, port) not in self.server.osc_clients:
			self.server.osc_clients[(ip, port)] = udp_client.SimpleUDPClient(ip, port)
			self._debug('success')
		else:
			self._debug('failure')

	def osc_remove_client(self, address, ip, port):
		"""
		Removes an OSC client.
		
		OSC listen: /remove

		:param str ip: the client ip to connect to 
		:type ip: str 
		:param int port: the client port to connect to
		:type port: int 

		"""

		ip = str(ip)
		port = int(port)

		self._debug('removing client', ip+':'+str(port))
		if (ip, port) in self.server.osc_clients:
			del self.server.osc_clients[(ip, port)]
			self._debug('success')
		else:
			self._debug('failure')


	def broadcast(self, address, data):
		self._debug('broadcasting to', address)

		for key, value in self.server.osc_clients.items():
			value.send_message(address, data)