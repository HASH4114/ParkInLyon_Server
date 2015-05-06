import MySQLdb as mdb
# Care MySQLdb output is latin1 (iso-8859-1) instead of utf8
from math import sqrt,sin,cos,atan2,pi
from config import *
import time
import requests
import json
import pprint
import sys
import re
import logger

parkings_cache = []
last_update = 0

def closestParking(lat,lon,nb_parking=3):
	lat,lon = float(lat),float(lon)
	global parkings_cache
	global last_update
	if len(parkings_cache) == 0 or (time.time() - last_update) > 10*60:
		logger.debug("Load parkings from DB")
		parkings = getAllParkings()
		parks_ordo = []
		for park in parkings:
			parks_ordo.append({'dist': diff_km(lat,lon,park[2],park[3]), 'id': park[0],'name': park[1].decode('iso-8859-1'),'posx': park[2],'posy': park[3],'address': park[4],'town': park[5], 'nbPlaces': park[6]})
		parkings_cache = sorted(parks_ordo, key=lambda k: k['dist'])
		last_update = time.time()
	return parkings_cache[:nb_parking]

# calcul diff lat lon as km
def diff_km(lat_0,lon_0,lat_1,lon_1):
	lat_0,lon_0,lat_1,lon_1 = [((coord * pi) /180) for coord in [lat_0,lon_0,lat_1,lon_1]]
	dlon = lon_1-lon_0
	dlat = lat_1-lat_0
	a = (sin(dlat/2)**2) + cos(lat_0) * cos(lat_1) * (sin(dlon/2)**2)
	c = 2 * atan2(sqrt(a),sqrt(1-a))
	return 6373 * c

# return an array
def getAllParkings():
	con = None
	try:
		con = mdb.connect('localhost', MYSQL_user, MYSQL_password, MYSQL_database)
		cur = con.cursor()
		cur.execute("SELECT id, name, posx, posy,address,town,nbPlaces FROM parking")
		return cur.fetchall()

	except mdb.Error, e:
		logger.error("Error %d: %s" % (e.args[0],e.args[1]))

	finally:
		if con:
			con.close()

# parse (a,b) in string
def parse_commas(string_param):
	try :
		searchObj = re.search( r'\(\s*(-?[0-9]+\.[0-9]+)\s*,\s*(-?[0-9]+\.[0-9]+)\s*\)\s*', string_param)
		return [float(searchObj.group(1)),float(searchObj.group(2))]
	except:
		logger.warn("Regex fail !")
		return ['err','err']

def sendRequest(depLat, depLon, endLat, endLon, requestType = "toDest"):

        headers = {'Accept': 'application/json'}
        params = { "fromPlace": str(depLat) + "," + str(depLon), "toPlace": str(endLat) + "," + str(endLon)}
        if requestType == "toPark":
                params["mode"] = "CAR"
        url = URL_OPEN_TRIP_PLANNER+"routers/default/plan"

        return requests.get(url, headers=headers, params = params).text


def merge(tabJson):
	#Main objects
	imported_json = []
	merged_routes_json = []

	#List of points part
	list_points = []
	list_points_object={}

	#Parts of itinerary just thoughtlessly copied
	leg=[]
	legs=[]
	legs_object = {}

	#Route_summary part
	route_summary = []
	route_summary_object= {}
	start_point = {}
	end_point = {}
	total_distance = {}
	total_time = {}

	temp_distance = 0
	temp_time = 0
	temp_name_file=""


	for i in range(1,len(tabJson)):
		imported_json.append(json.loads(tabJson[i]))


	for i in range(0, len(imported_json)):


		temp_itinerary = imported_json[i]["plan"]["itineraries"][1]


		for j in range(0,len(temp_itinerary["legs"])) :
			leg = temp_itinerary["legs"][j]
			temp_distance += leg["distance"]
			legs.append(leg)

			if leg["mode"] in ("BUS", "SUBWAY", "TRAM"):
				if j == 1 :
					list_points.append({"lat": temp_itinerary["legs"][0]["from"]["lat"], "lon":temp_itinerary["legs"][0]["from"]["lon"],"mode":leg["mode"]})
				list_points.append({"lat": leg["to"]["lat"], "lon":leg["to"]["lon"],"mode":leg["mode"]})
			elif leg ["mode"] in ("WALK","CAR"):
				for k in range (0, len(leg["steps"])):
					step = leg["steps"][k]
					list_points.append({"lat": step["lat"], "lon":step["lon"], "mode":leg["mode"]})
				list_points.append({"lat": leg["to"]["lat"], "lon": leg["to"]["lon"], "mode" : leg["mode"]})
		temp_time += temp_itinerary["duration"]

		



	#Filling the different variables with the merged values

	#ROUTE SUMMARY
	total_distance["total_distance"] = temp_distance
	total_time["total_time"] = temp_time
	start_point ["start_point"] = imported_json[0]["plan"]["from"]["name"]
	end_point["end_point"] = imported_json[len(imported_json)-1]["plan"]["to"]["name"]
	route_summary.append(start_point)
	route_summary.append(end_point)
	route_summary.append(total_time)
	route_summary.append(total_distance)

	#ALL POINTS
	legs_object["legs"] = legs
	route_summary_object["route_summary"] = route_summary
	list_points_object["list_points"] = list_points

	#Final JSON
	merged_routes_json.append(legs_object)
	merged_routes_json.append(list_points_object)
	merged_routes_json.append(route_summary_object)

	#Registering
	return merged_routes_json
	

def get_parking_by_name(park_name):
	con = None
	try:
		con = mdb.connect('localhost', MYSQL_user, MYSQL_password, MYSQL_database)
		cur = con.cursor()
		cur.execute("SELECT id, name, posx, posy,address,town,nbPlaces FROM parking WHERE LOWER(name) LIKE '%%%s%%'" % (park_name.replace("'","").lower()))
		parkings = cur.fetchall()
		return [{'id': park[0],'name': park[1].decode('iso-8859-1'),'posx': park[2],'posy': park[3],'address': park[4],'town': park[5], 'nbPlaces': park[6]} for park in parkings]
	except mdb.Error, e:
		logger.error("Error %d: %s" % (e.args[0],e.args[1]))
	finally:
		if con:
			con.close()
