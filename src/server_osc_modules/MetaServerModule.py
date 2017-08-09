from .OscModule import OscModule

from subprocess import Popen
import sys
import signal

class InnerServer(object):
	def __init__(self, process_name):
		self.proc = None
		self.process_name = process_name

	def start(self, arguments):
		if self.proc is None:
			command = [self.process_name]
			for k in arguments.keys():
				command.append('--'+k)
				command.append(str(arguments[k]))

			self.proc = Popen(command, stdout=sys.stdout, stderr=sys.stderr)

	def stop(self):
		if self.proc is not None:
			self.proc.send_signal(signal.SIGINT)
			self.proc.wait()
			self.proc = None

	def restart(self, arguments):
		self.stop()
		self.start(arguments)



class MetaServerModule(OscModule):

	"""
	ServerModule class. Implements OSC routes related to this OSC server internal mechanics
	"""

	@staticmethod
	def get_name():
		return 'METASERVER'

	def __init__(self, server, base_topic, debug=False):
		super(MetaServerModule, self).__init__(server=server, base_topic=base_topic, debug=debug)

	def routes(self):
		self.add_route('/restart', self.osc_restart)

	def osc_restart(self, address, *args):
		"""
		Restarts the server

		OSC listen: /restart
		"""

		self._debug('restarting server')
		self.server.inner_server.restart({
			'ip': self.server.args.ip,
			'port': self.server.args.inner_port
			})

	def start(self):
		self.server.inner_server = InnerServer('./inner_server.py')
		self._debug('starting server')
		self.server.inner_server.start({
			'ip': self.server.args.ip,
			'port': self.server.args.inner_port
			})

