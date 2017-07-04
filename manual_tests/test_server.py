#!/usr/bin/env python3

from pythonosc import dispatcher
from pythonosc import osc_server

dispatcher = dispatcher.Dispatcher()

dispatcher.map('*', print)

server = osc_server.ThreadingOSCUDPServer(
	('localhost', 8787),
	dispatcher
	)

server.serve_forever()