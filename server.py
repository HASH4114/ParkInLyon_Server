from config import *
from functions import *
import logger
import sys
import requests
import json
import functions
import time
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
	return "Server INFO <br />%s<br />Remote Server INFO <br />%s" % (infos,infos_remote)


@app.route('/parkings/list')
def listParking():
	coords = request.args.get('fromPlace','')
	parkings = []
	x,y = parse_commas(coords)
	if x == 'err':
		return "Erreur Argument !"
	parkings = closestParking(x,y)
	if len(parkings) == 0:
		return "[]"
	return jsonify(results=parkings)


@app.route('/search')
def searchParking():
	park_name = request.args.get('parking','')
	if park_name == '':
		return "Erreur Argument"
	results = get_parking_by_name(park_name)
	if len(results) == 0:
		return "[]"
	return jsonify(results=results)


@app.route('/plan')
def route():
	itiList = []
	
	departurePoint = request.args.get('fromPlace', '')
	depLat,depLon = parse_commas(departurePoint)
	endPoint = request.args.get('toPlace', '')
	endLat,endLon = parse_commas(endPoint)

	if 'err' == depLat or 'err' == endLat:
		return "Erreur Argument !"
	parkingList = functions.closestParking(depLat, depLon)
	for parking in parkingList:
		park_iti = sendRequest(depLat, depLon, parking['posx'], parking['posy'], "toPark")
		dest_iti = sendRequest(parking['posx'], parking['posy'], endLat, endLon)
		itiList.append(functions.merge([park_iti, dest_iti]))
	#Compare the itineraries
	return jsonify(results=itiList)


if __name__ == '__main__':
	logger.info("Starting ...")
	if not URL_OPEN_TRIP_PLANNER:
		logger.error("Please specify URL_OPEN_TRIP_PLANNER in config.py")
	if DEBUG:
		app.run(host='0.0.0.0',port=8080,debug=True)
	else:
		app.run(host='0.0.0.0',port=8080,threaded=True)

