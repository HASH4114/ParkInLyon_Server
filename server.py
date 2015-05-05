from config import *
import logger
import sys
import requests
from flask import Flask,jsonify, request
import json

app = Flask(__name__)


@app.route('/')
def running():
	i = {'i': 2 }
	resp = Response(response=i, status=200, mimetype="application/json")
	
	return 'Running !'

@app.route('/sysinfo')
def sysinfo():
	infos = ""
	if 'linux' in sys.platform:
		# todo
	infos_remote = ""
	try:
		infos_remote = requests.get("%s" % URL_OPEN_TRIP_PLANNER).text
	except:
		infos_remote = "Not Responding"
		logger.warn("OTP server %s" % infos_remote)
	return "Server INFO <br />%s<br />Remote Server INFO <br />%s" % (infos,infos_remote)


@app.route('/parkings/list')
def listParking():
	
	parkingList = closestParking(departurePoint, nbParking)
	
	a = json.dumps({'name':"Parking bidon", 'lat': 48.11022, 'lon': -1.66929, 'place': 43})
	return a
	
	
@app.route('/plan')
def route():
	itiList = []
	
	departurePoint = request.args.get('fromPlace', '')
	depLat = float(departurePoint.split(',')[0])
	depLon = float(departurePoint.split(',')[1])
	endPoint = request.args.get('toPlace', '')
	endLat = float(departurePoint.split(',')[0])
	endLon = float(departurePoint.split(',')[1])
	nbParking = request.args.get('numIti', '')

	parkingList = closestParking(departurePoint, nbParking)
	
	for parking in parkingList:
		park_iti = sendRequest(departurePoint, parking, "toPark")
		dest_iti = sendRequest(parking, endPoint)
		#Merge and put in data
		itiList.append(merge(park_iti, dest_iti))
	
	#Compare the itineraries
	
	return flask.jsonify(itiList)
	

	
def sendRequest(startPoint, endPoint, requestType = "toDest"):
	
	headers = {'Accept': 'application/json'}
	url = "http://92.222.74.70/otp/routers/default/plan?fromPlace=" + str(start[lat]) + ",%20" + str(start[lon]) + "&toPlace=" + str(end[lat]) + ",%20" + str(end[lon])
	
	if requestType == "toPark":
		url += "&mode=CAR"
	
	return json.loads(requests.get(url, headers=headers).text)

def getCoordinates(point):
	return 1,2
	
	
#todo
@app.route('/aaa/<username>')
def show_user_profile(username):
	# API OTP : 
	return 'User %s' % username


if __name__ == '__main__':
	logger.info("Starting ...")
	if not URL_OPEN_TRIP_PLANNER:
		logger.error("Please specify URL_OPEN_TRIP_PLANNER in config.py")
	app.run(debug=True, host='0.0.0.0',port=8080)

'''
API du Serveur:








'''
