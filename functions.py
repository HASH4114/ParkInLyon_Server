import MySQLdb as mdb
from math import sqrt
from config import *

def closestParking(lat,long,nb_parking=3):
	lat,long = float(lat),float(long)
	parkings = getAllParkings()
	parks_ordo = []
	for park in parkings:
		parks_ordo.append({'dist': sqrt((lat-park[2])**2+(long-park[3])**2), 'id': park[0],'name': park[1],'posx': park[2],'posy': park[3]})
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

