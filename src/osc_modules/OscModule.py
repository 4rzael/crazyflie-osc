import re
import sys

from functools import wraps

from colorama import Fore, Style
from .osc_validators import osc_requires

def regexed(regex):
	def decorator(method):
		@wraps(method)
		def wrapper(address, *args):
			# switch every {name} to "(P<name>.*)" in order to make a real regex
			pattern = re.sub('\{(.+?)\}', '(?P<\\1>.+)', regex)
			pattern = '^' + pattern + '$'
			# then match the path to the regex
			m = re.match(pattern, address)
			# The python-osc matcher is not perfect so we make it more restrictive here
			if m is not None:
				regex_args = m.groupdict()
				return method(address, *args, **regex_args)
		return wrapper
	return decorator


def regex_to_topic(regex):
	return re.sub('\{.+?\}', '*', regex)


class OscModule(object):

	@staticmethod
	def get_name():
		raise NotImplementedError


	"""docstring for OscModule"""
	def _topic_reg(self, topic):
		if topic[0] is not '/':
			topic = '/' + topic
		return self.base_topic + str(topic)


	def __init__(self, server, base_topic, debug=False):
		"""
		OscModule constructor

		:param base_topic: the topic of this module. Every routes in it will be relative to this one.
		:type base_topic: str.
		:param debug: configure either the module should print debug messages.
		:type debug: bool.
		"""
		self.base_topic = str(base_topic)
		# remove potential trailing / and add a potential / at the beginning
		if self.base_topic[-1] is '/':
			self.base_topic = self.base_topic[:-1]
		self.server = server
		self.debug = debug
		self.dispatcher = None

		self._routes = []


	def add_route(self, sub_topic, callback):
		"""
		Add a new route to the server (relative to the module base_topic).

		:param sub_topic: the topic (relative to base_topic) of this route.
		:type sub_topic: str.
		:param callback: the route handler.
		:type callback: function.
		"""
		full_topic_regex = self._topic_reg(sub_topic)
		full_topic = regex_to_topic(full_topic_regex)
		self.dispatcher.map(full_topic, regexed(full_topic_regex)(callback))
		self._routes.append(full_topic_regex)


	def _debug(self, *args):
		"""
		Print a debug message (todo: also send to an OSC topic).
		"""
		if self.debug:
			args = args + (Style.RESET_ALL,)
			print(Fore.YELLOW + '['+self.get_name()+' DEBUG]', *args)


	def _error(self, *args):
		"""
		Print an error message on stderr (todo: also send to an OSC topic).
		"""
		args = args + (Style.RESET_ALL,)
		print(Fore.RED + '['+self.get_name()+' ERROR]', *args, file=sys.stderr)


	@osc_requires('CLIENT')
	def _send(self, topic, data):
		self.server.get_module('CLIENT').broadcast(self._topic_reg(topic), data)


	def __call__(self, dispatcher):
		"""
		Builds the routes of this module.

		:param dispatcher: the python-osc dispatcher.
		:type dispatcher: Dispatcher.
		"""
		self.dispatcher = dispatcher
		self.routes()
		self._debug('routes built on', self.base_topic)
		self._debug('routes list')
		for route in self._routes:
			self._debug('>', route)
		return dispatcher

	# def add_submodule(self, submodule, subtopic, *args, **kwargs):
	# 	if self.dispatcher is None:
	# 		print('Cannot add submodule : no dispatcher found')
	# 		return
	# 	sm = submodule(base_topic=self._topic(subtopic), *args, **kwargs)
	# 	return sm(lambda dispatcher:dispatcher)(self.dispatcher)


	def routes(self):
		"""
		Add your routes here with self.add_route() calls.
		"""
		raise NotImplementedError