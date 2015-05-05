import MySQLdb as mdb
# Care MySQLdb output is latin1 (iso-8859-1) instead of utf8
from math import sqrt
from config import *
import json
import pprint
import sys
import re
import logger

def closestParking(lat,lon,nb_parking=3):
	lat,lon = float(lat),float(lon)
	parkings = getAllParkings()
	parks_ordo = []
	for park in parkings:
		parks_ordo.append({'dist': sqrt((lat-park[2])**2+(lon-park[3])**2), 'id': park[0],'name': park[1].decode('iso-8859-1'),'posx': park[2],'posy': park[3]})
	parks_ordo = sorted(parks_ordo, key=lambda k: k['dist'])
	return parks_ordo[:nb_parking]



#return an array
def getAllParkings():
	try:
		con = mdb.connect('localhost', MYSQL_user, MYSQL_password, MYSQL_database)
		cur = con.cursor()
		cur.execute("SELECT id, name, posx, posy FROM parking")
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
	params = {'fromPlace': str(start[lat]) + ",%20" + str(start[lon]), 'toPlace': str(end[lat]) + ",%20" + str(end[lon])}
	url = "http://92.222.74.70/otp/routers/default/plan"
	
	if requestType == "toPark":
		params['mode'] = 'CAR'
	
	return json.loads(requests.get(url,params=params, headers=headers).text)


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
		imported_json.append(tabJson[i])


	for i in range(0, len(imported_json)):


		temp_itinerary = imported_json[i]["plan"]["itineraries"][1]


		for j in range(0,len(temp_itinerary["legs"])) :
			leg = temp_itinerary["legs"][j]
			temp_distance += leg["distance"]
			legs.append(leg)

			if leg["mode"] == ("BUS" or "SUBWAY" or "TRAM"):
				if j == 1 :
					list_points.append({"lat": temp_itinerary["legs"][0]["from"]["lat"], "long":temp_itinerary["legs"][0]["from"]["lon"]})
				list_points.append({"lat": leg["to"]["lat"], "long":leg["to"]["lon"]})
			elif leg ["mode"]== ("WALK" or "CAR"):
				for k in range (0, len(leg["steps"])):
					step = leg["steps"][k]
					list_points.append({"lat": step["lat"], "long":step["lon"]})  	
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
	with open('merged_routes.json', 'w') as f:
		f.write(json.dumps(merged_routes_json))

