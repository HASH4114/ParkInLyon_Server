from config import *
from functions import *
import logger
import sys
import requests
import json
import functions
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
	return jsonify(results=parkings)

	
	
@app.route('/plan')
def route():
	itiList = []
	
	departurePoint = request.args.get('fromPlace', '')
	depLat,depLon = parse_commas(departurePoint)
	endPoint = request.args.get('toPlace', '')
	endLat,endLon = parse_commas(departurePoint)

	if 'err' == depLat or 'err' == endLat:
		return "Erreur Argument !"

	parkingList = functions.closestParking(depLat, depLon)
	
	for parking in parkingList:
		park_iti = sendRequest(depLat, depLon, parking['posx'], parking['posy'], "toPark")
		dest_iti = sendRequest(parking['posx'], parking['posy'], endLat, endLon)
		itiList.append(functions.merge([park_iti, dest_iti]))
	#Compare the itineraries
	return jsonify(results=itiList)

def sendRequest(depLat, depLon, endLat, endLon, requestType = "toDest"):
	
	headers = {'Accept': 'application/json'}
	params = { "fromPlace": str(depLat) + "," + str(depLon), "toPlace": str(endLat) + "," + str(endLon)}
	if requestType == "toPark":
		params["mode"] = "car"	
	url = "http://92.222.74.70/otp/routers/default/plan"

	return requests.get(url, headers=headers, params = params).text


if __name__ == '__main__':
	logger.info("Starting ...")
	if not URL_OPEN_TRIP_PLANNER:
		logger.error("Please specify URL_OPEN_TRIP_PLANNER in config.py")
	if DEBUG:
		app.run(host='0.0.0.0',port=8080,debug=True)
	else:
		app.run(host='0.0.0.0',port=8080)

