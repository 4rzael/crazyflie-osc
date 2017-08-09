#!/usr/bin/env python3

"""
Main server code
dispatches requests to correct modules
"""
import argparse

from server_osc_modules import MetaServerModule

from pythonosc import dispatcher
from pythonosc import osc_server

from threading import Thread

class MetaServer(object):
	"""
	The meta-server. Calls the inner server and handle its restarting abilities
	"""
	def __init__(self):
		self._osc_server = None
		self._osc_server_thread = None

		self.modules = {}

		self.dispatcher = dispatcher.Dispatcher()

		self.inner_server = None
		self.args = None


	def build_routes(self):
		"""
		Build the meta-server routes.
		Routes :
		/server/* -> See MetaServerModule
		"""

		self.modules = {
			MetaServerModule.get_name():
				MetaServerModule(base_topic='/server', server=self, debug=True),
		}

		for module in self.modules:
			self.modules[module](self.dispatcher)


	def run(self, args):
		self.args = args
		self.ip = args.ip
		self.port = args.meta_port
		self._osc_server = osc_server.ThreadingOSCUDPServer(
			(self.ip, self.port), self.dispatcher)
		print("Serving on {}".format(self._osc_server.server_address))
		self._osc_server_thread = Thread(target=self._osc_server.serve_forever)
		self._osc_server_thread.start()

		for module in self.modules:
			self.modules[module].start()

		self._osc_server_thread.join()


	def stop(self):
		if self._osc_server:
			print('stopping server')
			for module in self.modules.values():
				module.stop()
			self._osc_server.shutdown()

if __name__ == "__main__":

	try:
		from colorama import init as colorama_init
		colorama_init()
	except:
		pass

	parser = argparse.ArgumentParser()
	parser.add_argument("--ip",
		default="0.0.0.0", help="The ip to listen on")
	parser.add_argument("--meta_port",
		type=int, default=5006, help="The port to listen on for the meta server")
	parser.add_argument("--inner_port",
		type=int, default=5005, help="The port to listen on for the inner server")

	args = parser.parse_args()

	server = None

	# ctrl+c killing
	import signal
	import sys
	import os
	def sigint_handler(sig, frame):
		global server
		if server is not None:
			server.stop()
			server = None
		else:
			print('Escalating to SIGTERM')
			os.kill(os.getpid(), signal.SIGTERM)

	signal.signal(signal.SIGINT, sigint_handler)

	server = MetaServer()
	server.build_routes()
	server.run(args)
