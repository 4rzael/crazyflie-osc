from .OscModule import OscModule

from subprocess import Popen
import sys
if sys.platform is 'win32':
	from subprocess import CREATE_NEW_PROCESS_GROUP
else:
	CREATE_NEW_PROCESS_GROUP = 0
import signal

class InnerServer(object):
	def __init__(self, process_name, *args):
		self.proc = None
		self.process_name = process_name
		self.args = list(args)

	def start(self, arguments):
		if self.proc is None:
			command = [self.process_name] + self.args
			for k in arguments.keys():
				command.append('--'+k)
				command.append(str(arguments[k]))

			self.proc = Popen(command, stdout=sys.stdout, stderr=sys.stderr, creationflags=CREATE_NEW_PROCESS_GROUP)

	def stop(self):
		if self.proc is not None:
			try:
				self.proc.send_signal(signal.SIGINT)
			except:
				self.proc.kill()
			finally:
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
		self.server.inner_server = InnerServer('python', './inner_server.py')
		self._debug('starting server')
		self.server.inner_server.start({
			'ip': self.server.args.ip,
			'port': self.server.args.inner_port
			})

	def stop(self):
		self.server.inner_server.stop()
