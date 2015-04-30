import sys
import time
from config import *

def debug(msg):
	"""Writes the message to the log file using the ``DEBUG`` level."""
	write(msg, 'DEBUG')

def info(msg, also_console=True):
	"""Writes the message to the log file using the ``INFO`` level.

	If ``also_console`` argument is set to ``True``, the message is
	written both to the log file and to the console.
	"""
	write(msg, 'INFO',also_console)

def warn(msg):
	"""Writes the message to the log file using the ``WARN`` level."""
	write(msg, 'WARN')

def error(msg):
	"""Writes the message to the log file using the ``ERROR`` level."""
	write(msg, 'ERROR',also_console=True)
	info("Exiting !")
	sys.exit(1)

def write(msg,level,also_console=False):
	if 'LOG_FILE' in globals():
		log_file = open(LOG_FILE,'ab')
		log_file.write('%s	[%s] - %s\n' % (time.strftime('%d/%m/%y %H:%M',time.localtime()),level,msg))
		log_file.close()
		if also_console:
			console("[%s] - %s" % (level,msg))
	else :
		console("[%s] - %s" % (level,msg))

def console(msg, newline=True):
	"""Writes the message to the console.

	If the ``newline`` argument is ``True``, a newline character is
	automatically added to the message.

	By default the message is written to the standard output stream.
	Using the standard error stream is possibly by giving the ``stream``
	argument value ``'stderr'``. This is a new feature in RF 2.8.2.
	"""
	sys.stdout.write(msg + ('\n' if newline else ''))