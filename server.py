from config import *
import logger
import sys
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def running():
	return 'Running !'

@app.route('/sysinfo')
def sysinfo():
	infos = ""
	if 'linux' in sys.platform:
		import linux_sysinfo as sysinfo
		infos = sysinfo.memory_available()
		logger.debug(infos)
	infos_remote = ""
	try:
		infos_remote = requests.get("%s" % URL_OPEN_TRIP_PLANNER).text
	except:
		infos_remote = "Not Responding"
		logger.warn("OTP server %s" % infos_remote)
	return "Server INFO <br />%s<br />Remote Server INFO <br />%s" % (infos,infos_remote)

#todo
@app.route('/aaa/<username>')
def show_user_profile(username):
	# API OTP : 
	return 'User %s' % username


if __name__ == '__main__':
	logger.info("Starting ...")
	if not URL_OPEN_TRIP_PLANNER:
		logger.error("Please specify URL_OPEN_TRIP_PLANNER in config.py")
	app.run(host='0.0.0.0',port=8080)

'''
API du Serveur:








'''
