#!/usr/bin/env python3

"""
Main server code
dispatches requests to correct modules
"""
import argparse

from osc_modules import *

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

from threading import Thread

import cflib

class Server(object):
	"""
	The main server
	"""
	def __init__(self):
		self._osc_server = None
		self._osc_server_thread = None

		self.modules = {}

		self.dispatcher = dispatcher.Dispatcher()
		# DroneModule
		self.drones = utils.ThreadSafeDict();
		# ClientModule
		self.osc_clients = {}
		# LpsModule
		self.lps_node_number = 8
		self.lps_positions = [None] * self.lps_node_number


	def get_module(self, name):
		return self.modules[name] if name in self.modules else None


	def build_routes(self):
		"""
		Build the server routes.
		Routes :
		/server/* -> See ServerModule
		/client/* -> See ClientModule
		/crazyflie/* -> See CrazyflieModule
		/lps/* -> See LpsModule
		/log/* -> See LogModule
		/param/* -> See ParamModule
		"""

		self.modules = {
			ServerModule.get_name():
				ServerModule(base_topic='/server', server=self, debug=True),

			ClientModule.get_name():
				ClientModule(base_topic='/client', server=self, debug=False),
			CrazyflieModule.get_name():
				CrazyflieModule(base_topic='/crazyflie', server=self, debug=True),
			LpsModule.get_name():
				LpsModule(base_topic='/lps', server=self, debug=True),
			LogModule.get_name():
				LogModule(base_topic='/log', server=self, debug=True),
			ParamModule.get_name():
				ParamModule(base_topic='/param', server=self, debug=True),

			#TestModule.get_name():
			#	TestModule(base_topic='/test', server=self, debug=False),
		}

		for module in self.modules:
			self.modules[module](self.dispatcher)


	def run(self, args):
		self.ip = args.ip
		self.port = args.port
		self._osc_server = osc_server.ThreadingOSCUDPServer(
			(args.ip, args.port), self.dispatcher)
		print("Serving on {}".format(self._osc_server.server_address))
		self._osc_server_thread = Thread(target=self._osc_server.serve_forever)
		self._osc_server_thread.start()
		self._osc_server_thread.join()
		self._osc_server_thread = None
		self._osc_server = None


	def stop(self):
		if self._osc_server:
			print('stopping server', self.drones)
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
	parser.add_argument("--port",
		type=int, default=5005, help="The port to listen on")
	args = parser.parse_args()

	cflib.crtp.init_drivers(enable_debug_driver=False)
	server = None

	# ctrl+c killing
	import signal
	import sys
	import os
	__main_should_run = True
	def sigint_handler(sig, frame):
		global server
		global __main_should_run
		__main_should_run = False
		if server is not None:
			server.stop()
			server = None
		else:
			os.kill(os.getpid(), signal.SIGTERM)

	signal.signal(signal.SIGINT, sigint_handler)

	while __main_should_run:
		server = Server()
		server.build_routes()
		server.run(args)
	os.kill(os.getpid(), signal.SIGTERM)
