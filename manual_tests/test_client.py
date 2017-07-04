#!/usr/bin/env python3

"""
Test client for osc. Reads from stdin and send osc from it
"""
import argparse
import sys
from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client

def is_int(s):
	try:
		int(s)
		return True
	except:
		return False

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
	'str[]': lambda lws: lws,
	'int': lambda lws: int(lws[0]),
	'int[]': lambda lws: [int(lw) for lw in lws],
	'float': lambda lws: float(lws[0]),
	'float[]': lambda lws: [float(lw) for lw in lws],
	'none': lambda lws: None,
	'blob': clever,
	'bool': lambda lws: bool(int(lws[0])),
}

defines = {}

def run_one(client, line):
	global defines

	if line[-1] is '\n':
		line = line[:-1]

	#remove comments
	line = line.split(';', 1)[0]


	#use defines
	line = ' ' + line + ' '
	for (k,v) in defines.items():
		line = line.replace(' #'+k+' ', v)

	#trim
	line = line.strip()

	if len(line) is 0:
		return

	try:
		linewords = line.split(' ')
		# remove useless things
		linewords = [w for w in linewords if len(w) > 0]
		print(linewords)

		# WAIT directive (waits for n milliseconds)
		if len(linewords) is 2 and linewords[0] == '#WAIT' and is_int(linewords[1]):
			sleep(float(int((linewords[1]))) / 1000.0)
		elif len(linewords) is 2 and linewords[0] == '#IMPORT':
			run_from_file(client, linewords[1])
		elif len(linewords) >= 3 and linewords[0] == '#DEFINE':
			defines[linewords[1]] = ' '.join(linewords[2:])
		elif len(linewords) is 2 and linewords[0] == '#UNDEFINE':
			if linewords[1] in defines:
				del defines[linewords[1]]
		else:
			topic = linewords[0]
			if len(linewords) is 1:
				data = 'NO ARGS PROVIDED'
			else:
				data_type = linewords[1]
				data = type_to_func[data_type](linewords[2:])
			client.send_message(topic, data)
	except Exception as e:
		print(e)
	

def run_interactive(client):
	for line in sys.stdin:
		run_one(client, line)

def run_from_file(client, file):
	try:
		with open(file, 'r') as f:
			for line in f.readlines():
				print(line[:-1] if line[-1] is '\n' else line)
				run_one(client, line)
	except Exception as e:
		print(e)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", default="127.0.0.1",
		help="The ip of the OSC server")
	parser.add_argument("--port", type=int, default=5005,
		help="The port the OSC server is listening on")
	parser.add_argument('--file', type=str, default=None,
		help='the scripting file to run before interactive terminal.')
	args = parser.parse_args()

	client = udp_client.SimpleUDPClient(args.ip, args.port)
	print('connected to', str(args.ip)+':'+str(args.port))

	if args.file is not None:
		run_from_file(client, args.file)
	run_interactive(client)

