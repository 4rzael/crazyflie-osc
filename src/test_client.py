#!/usr/bin/env python3

"""
Test client for osc. Reads from stdin and send osc from it
"""
import argparse
import sys

from pythonosc import osc_message_builder
from pythonosc import udp_client

def clever(lws):
	def inner(lw):
		try:
			return float(lw)
		except:
			try:
				return int(lw)
			except:
				return str(lw)
	return map(inner, lws)

type_to_func = {
	'str': lambda lws: ' '.join(lws),
	'int': lambda lws: int(lws[0]),
	'int[]': lambda lws: [int(lw) for lw in lws],
	'float': lambda lws: float(lws[0]),
	'float[]': lambda lws: [float(lw) for lw in lws],
	'none': lambda lws: None,
	'blob': clever
}

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", default="127.0.0.1",
		help="The ip of the OSC server")
	parser.add_argument("--port", type=int, default=5005,
		help="The port the OSC server is listening on")
	args = parser.parse_args()

	client = udp_client.SimpleUDPClient(args.ip, args.port)
	print('connected to', str(args.ip)+':'+str(args.port))

	for line in sys.stdin:
		try:
			linewords = line.split(' ')
			topic = linewords[0]
			data_type = linewords[1]
			data = type_to_func[data_type](linewords[2:])
			client.send_message(topic, data)
		except Exception as e:
			print(e)
			pass