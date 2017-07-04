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

import cflib

class Server(object):
	"""
	The main server
	"""
	def __init__(self):
		self.modules = {}

		self.dispatcher = dispatcher.Dispatcher()
		# DroneModule
		self.drones = {}
		# ClientModule
		self.osc_clients = {}
		# LpsModule
		self.lps_node_number = 8


	def get_module(self, name):
		return self.modules[name] if name in self.modules else None


	def build_routes(self):
		"""
		Build the server routes.
		Routes :
		/client/* -> See ClientModule
		/crazyflie/* -> See CrazyflieModule
		/lps/* -> See LpsModule
		"""
		self.modules = {
			ClientModule.get_name():
				ClientModule(base_topic='/client', server=self, debug=True),
			CrazyflieModule.get_name():
				CrazyflieModule(base_topic='/crazyflie', server=self, debug=True),
			LpsModule.get_name():
				LpsModule(base_topic='/lps', server=self, debug=True),
			LogModule.get_name():
				LogModule(base_topic='/log', server=self, debug=True),
			ParamModule.get_name():
				ParamModule(base_topic='/param', server=self, debug=True),
		}

		for module in self.modules:
			self.modules[module](self.dispatcher)


	def run(self, args):
		self.ip = args.ip
		self.port = args.port
		server = osc_server.ThreadingOSCUDPServer(
			(args.ip, args.port), self.dispatcher)
		print("Serving on {}".format(server.server_address))
		cflib.crtp.init_drivers(enable_debug_driver=False)
		server.serve_forever()
		

if __name__ == "__main__":

	try:
		from colorama import init as colorama_init
		colorama_init()
	except:
		pass

	parser = argparse.ArgumentParser()
	parser.add_argument("--ip",
		default="127.0.0.1", help="The ip to listen on")
	parser.add_argument("--port",
		type=int, default=5005, help="The port to listen on")
	args = parser.parse_args()

	server = Server()
	server.build_routes()
	server.run(args)
