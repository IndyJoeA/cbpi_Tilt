# -*- coding: utf-8 -*-
import threading
import time
from modules import cbpi
from modules.core.hardware import SensorPassive
from modules.core.props import Property

import bluetooth._bluetooth as bluez
import blescan

tilt_thread = None
tilt_cache = {}

TILTS = {
	'a495bb10c5b14b44b5121370f02d74de': 'Red',
	'a495bb20c5b14b44b5121370f02d74de': 'Green',
	'a495bb30c5b14b44b5121370f02d74de': 'Black',
	'a495bb40c5b14b44b5121370f02d74de': 'Purple',
	'a495bb50c5b14b44b5121370f02d74de': 'Orange',
	'a495bb60c5b14b44b5121370f02d74de': 'Blue',
	'a495bb70c5b14b44b5121370f02d74de': 'Yellow',
	'a495bb80c5b14b44b5121370f02d74de': 'Pink',
}

def calcGravity(gravity, unitsGravity):
	sg = round(float(gravity)/1000, 3)
	if unitsGravity == u"°P":
		# Source: https://en.wikipedia.org/wiki/Brix
		return round(((182.4601 * sg -775.6821) * sg + 1262.7794) * sg - 669.5622, 2)
	elif unitsGravity == u"Brix":
		# Source: https://en.wikipedia.org/wiki/Brix
		return round(((182.4601 * sg -775.6821) * sg + 1262.7794) * sg - 669.5622, 2)
	else:
		return sg

def calcTemp(temp):
	f = float(temp)
	if cbpi.get_config_parameter("unit", "C") == "C":
		return round((f - 32) / 1.8, 2)
	else:
		return round(f, 2)

def distinct(objects):
	seen = set()
	unique = []
	for obj in objects:
		if obj['uuid'] not in seen:
			unique.append(obj)
			seen.add(obj['uuid'])
	return unique

def readTilt():
	global tilt_cache
	dev_id = 0
	try:
		logTilt("Starting Bluetooth connection")
		
		sock = bluez.hci_open_dev(dev_id)
		blescan.hci_le_set_scan_parameters(sock)
		blescan.hci_enable_le_scan(sock)	
	
		while True:
			beacons = distinct(blescan.parse_events(sock, 10))
			for beacon in beacons:
				if beacon['uuid'] in TILTS.keys():
					tilt_cache[TILTS[beacon['uuid']]] = {'Temp': beacon['major'], 'Gravity': beacon['minor']}
					logTilt("Tilt data received: Temp %s Gravity %s" % (beacon['major'], beacon['minor']))
			time.sleep(4)
	except Exception as e:
		logTilt("Error starting Bluetooth device, exception: %s" % str(e))

def logTilt(text):
	filename = "./logs/tilt.log"
	formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

	with open(filename, "a") as file:
		file.write("%s,%s\n" % (formatted_time, text))

@cbpi.sensor
class TiltHydrometer(SensorPassive):

	color = Property.Select("Tilt Color", options=["Red", "Green", "Black", "Purple", "Orange", "Blue", "Yellow", "Pink"])
	sensorType = Property.Select("Data Type", options=["Temperature", "Gravity"])
	unitsGravity = Property.Select("Gravity Units", options=["SG", "Brix", "°P"])

	def get_unit(self):
		if self.sensorType == "Temperature":
			return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"
		elif self.sensorType == "Gravity":
			return self.unitsGravity
		else:
			return " "
			
	def read(self):
		if tilt_cache[self.color] is not None:
			if self.sensorType == "Gravity":
				reading = calcGravity(tilt_cache[self.color]['Gravity'], self.unitsGravity)
			else:
				reading = calcTemp(tilt_cache[self.color]['Temp'])
			self.data_received(reading)
			
@cbpi.initalizer()
def init(cbpi):
	global tilt_thread	
	print "INITIALIZE TILT MODULE"
	
	tilt_thread = threading.Thread(name='readTilt', target=readTilt)
	tilt_thread.setDaemon(True)
	tilt_thread.start()
