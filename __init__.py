# -*- coding: utf-8 -*-
from multiprocessing import Process, Manager
import time
from modules import cbpi
from modules.core.hardware import SensorPassive
from modules.core.props import Property

import bluetooth._bluetooth as bluez
from . import blescan

import numpy as np

tilt_proc = None
tilt_manager = None
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

def add_calibration_point(x, y, field):
	if isinstance(field, str) and field:
		x1, y1 = field.split("=")
		x = np.append(x, float(x1))
		y = np.append(y, float(y1))
	return x, y

def calcGravity(gravity, unitsGravity):
	sg = float(gravity)/1000
	if unitsGravity == "Plato" or unitsGravity == "°P":
		# Source: https://en.wikipedia.org/wiki/Brix
		return ((135.997 * sg - 630.272) * sg + 1111.14) * sg - 616.868
	elif unitsGravity == "Brix" or unitsGravity == "°Bx":
		# Source: https://en.wikipedia.org/wiki/Brix
		return ((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622
	else:
		return sg

def calcTemp(temp):
	f = float(temp)
	if cbpi.get_config_parameter("unit", "C") == "C":
		return (f - 32) / 1.8
	else:
		return f

def calibrate(tilt, equation):
	return eval(equation)
	
def distinct(objects):
	seen = set()
	unique = []
	for obj in objects:
		if obj['uuid'] not in seen:
			unique.append(obj)
			seen.add(obj['uuid'])
	return unique

def readTilt(cache):
	dev_id = 0
	while True:
		try:
			logTilt("Starting Bluetooth connection")
		
			sock = bluez.hci_open_dev(dev_id)
			blescan.hci_le_set_scan_parameters(sock)
			blescan.hci_enable_le_scan(sock)	
	
			while True:
				beacons = distinct(blescan.parse_events(sock, 10))
				for beacon in beacons:
					if beacon['uuid'] in list(TILTS.keys()):
						cache[TILTS[beacon['uuid']]] = {'Temp': beacon['major'], 'Gravity': beacon['minor']}
						#logTilt("Tilt data received: Temp %s Gravity %s" % (beacon['major'], beacon['minor']))
				time.sleep(4)
		except Exception as e:
			logTilt("Error starting Bluetooth device, exception: %s" % str(e))

		logTilt("Restarting Bluetooth process in 10 seconds")
		time.sleep(10)

def logTilt(text):
	filename = "./logs/tilt.log"
	formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

	with open(filename, "a") as file:
		file.write("%s,%s\n" % (formatted_time, text))

@cbpi.sensor
class TiltHydrometer(SensorPassive):

	color = Property.Select("Tilt Color", options=["Red", "Green", "Black", "Purple", "Orange", "Blue", "Yellow", "Pink"], description="Select the color of your Tilt")
	sensorType = Property.Select("Data Type", options=["Temperature", "Gravity"], description="Select which type of data to register for this sensor")	
	unitsGravity = Property.Select("Gravity Units", options=["SG", "Brix", "°Bx", "Plato", "°P"], description="Converts the gravity reading to this unit if the Data Type is set to Gravity")
	x_cal_1 = Property.Text(label="Calibration Point 1", configurable=True, default_value="", description="Optional field for calibrating your Tilt. Enter data in the format uncalibrated=actual")
	x_cal_2 = Property.Text(label="Calibration Point 2", configurable=True, default_value="", description="Optional field for calibrating your Tilt. Enter data in the format uncalibrated=actual")
	x_cal_3 = Property.Text(label="Calibration Point 3", configurable=True, default_value="", description="Optional field for calibrating your Tilt. Enter data in the format uncalibrated=actual")
	calibration_equ = ""
	
	def init(self):
		# Load calibration data from plugin
		x = np.empty([0])
		y = np.empty([0])
		x, y = add_calibration_point(x, y, self.x_cal_1)
		x, y = add_calibration_point(x, y, self.x_cal_2)
		x, y = add_calibration_point(x, y, self.x_cal_3)
		
		# Create calibration equation
		if len(x) < 1:
			self.calibration_equ = "tilt"
		if len(x) == 1:
			self.calibration_equ = 'tilt + {0}'.format(y[0] - x[0])
		if len(x) > 1:
			A = np.vstack([x, np.ones(len(x))]).T
			m, c = np.linalg.lstsq(A, y)[0]
			self.calibration_equ = '{0}*tilt + {1}'.format(m, c)
			
		logTilt('Calibration equation: {0}'.format(self.calibration_equ))
	
	def get_unit(self):
		if self.sensorType == "Temperature":
			return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"
		elif self.sensorType == "Gravity":
			return self.unitsGravity
		else:
			return " "
			
	def read(self):
		if self.color in tilt_cache:
			if self.sensorType == "Gravity":
				reading = calcGravity(tilt_cache[self.color]['Gravity'], self.unitsGravity)
				reading = calibrate(reading, self.calibration_equ)
				reading = round(reading, 3)
			else:
				reading = calcTemp(tilt_cache[self.color]['Temp'])
				reading = calibrate(reading, self.calibration_equ)
				reading = round(reading, 2)
			self.data_received(reading)
			
@cbpi.initalizer(order=9999)
def init(cbpi):
	global tilt_proc
	global tilt_manager
	global tilt_cache	
	print("INITIALIZE TILT MODULE")
	
	tilt_manager = Manager()
	tilt_cache = tilt_manager.dict()

	tilt_proc = Process(name='readTilt', target=readTilt, args=(tilt_cache,))
	tilt_proc.daemon = True
	tilt_proc.start()
