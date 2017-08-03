import threading
from functools import wraps

# defines wether the dictionary can only be accessed with locking or not
THREADSAFEDICT_STRICT_MODE = False

def check_locked(method):
	if THREADSAFEDICT_STRICT_MODE is not True:
		return method
	else:
		@wraps(method)
		def wrapped(self, *args, **kwargs):
			if self._locked is False:
				raise Exception('ACCESS TO DICT WITHOUT LOCK')
			return method(self, *args, **kwargs)
		return wrapped

class ThreadSafeDict(dict) :
	def __init__(self, * p_arg, ** n_arg) :
		dict.__init__(self, * p_arg, ** n_arg)
		self._lock = threading.RLock()
		self._locked = False

	@check_locked
	def keys(self):
		return super(ThreadSafeDict, self).keys() 				

	@check_locked
	def items(self):
		return super(ThreadSafeDict, self).items() 				

	@check_locked
	def __contains__(self, key):
		return super(ThreadSafeDict, self).__contains__(key)

	@check_locked
	def __getitem__(self, key):
		return super(ThreadSafeDict, self).__getitem__(key) 				

	def __enter__(self) :
		self._lock.acquire()
		self._locked = True
		return self

	def __exit__(self, type, value, traceback) :
		self._lock.release()
		self._locked = False
