﻿from config import *
from functions import *
import logger
import sys
import requests
import json
import functions
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
	return "Server INFO <br />%s<br />Remote Server INFO <br />%s" % (infos,infos_remote)


@app.route('/parkings/list')
def listParking():
	
	point = request.args.get('fromPlace', '')
	lat = float(departurePoint.split(',')[0])
	lon = float(departurePoint.split(',')[1])
	
	return closestParking(lat,lon)
	
	
@app.route('/plan')
def route():
	itiList = []
	
	departurePoint = request.args.get('fromPlace', '')
	depLat = float(departurePoint.split(',')[0])
	depLon = float(departurePoint.split(',')[1])
	endPoint = request.args.get('toPlace', '')
	endLat = float(departurePoint.split(',')[0])
	endLon = float(departurePoint.split(',')[1])

	parkingList = functions.closestParking(depLat, depLon)
	
	for parking in parkingList:
		park_iti = sendRequest(depLat, depLon, parking[2], parking[3], "toPark")
		dest_iti = sendRequest(parking[2], parking[3], endLat, endLon)
		
		itiList.append(functions.merge([park_iti, dest_iti]))
	
	#Compare the itineraries
	
	return flask.jsonify(itiList)
	

	
def sendRequest(depLat, depLon, endLat, endLon, requestType = "toDest"):
	
	headers = {'Accept': 'application/json'}
	url = "http://92.222.74.70/otp/routers/default/plan?fromPlace=" + str(start[lat]) + ",%20" + str(start[lon]) + "&toPlace=" + str(end[lat]) + ",%20" + str(end[lon])
	
	if requestType == "toPark":
		url += "&mode=CAR"
	
	return json.loads(requests.get(url, headers=headers).text)

def getCoordinates(point):
	return 1,2


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
