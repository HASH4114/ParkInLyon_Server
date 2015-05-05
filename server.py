from config import *
from functions import *
import logger
import sys
import requests
import re
from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route('/')
def running():
	return 'Running !'

@app.route('/sysinfo')
def sysinfo():
	infos = ""
	if 'linux' in sys.platform:
		import psutil
		infos += "CPU : %d%%<br />" % (psutil.cpu_percent())
		infos += "Mem : %d%%<br />" % (psutil.virtual_memory()[2])
	infos_remote = ""
	try:
		infos_remote = requests.get("%s" % URL_OPEN_TRIP_PLANNER).text
	except:
		infos_remote = "Not Responding"
		logger.warn("OTP server %s" % infos_remote)
	return "<b>Server INFO </b><br />%s<br /><br /><b>Remote Server INFO </b><br />%s" % (infos,infos_remote)

'''Car itinerary to the closest non-full parking:
	/parkings?fromPlace=(lat,lon)
Params :
	fromPlace
	Optionnal :
		checkIfFull (default to yes, ex for no : the client wants to find a parking for later)
'''
@app.route('/parkings')
def API_parkings():
	# checkIfFull API integration for 4 parkings "relai"
	coords = request.args.get('fromPlace','')
	parkings = []
	try :
		searchObj = re.search( r'\(\s*(-?[0-9]+\.[0-9]+)\s*,\s*(-?[0-9]+\.[0-9]+)\s*\)\s*', coords)
		x = float(searchObj.group(1))
		y = float(searchObj.group(2))
	except:
		logger.warn("API_parkings regex fail !")
		return "Erreur argument !"
	parkings = closestParking(x,y)
	return jsonify(results=parkings)


if __name__ == '__main__':
	logger.info("Starting ...")
	if not URL_OPEN_TRIP_PLANNER:
		logger.error("Please specify URL_OPEN_TRIP_PLANNER in config.py")
	if DEBUG:
		app.run(host='0.0.0.0',port=8080,debug=True)
	else:
		app.run(host='0.0.0.0',port=8080)

