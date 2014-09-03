import gimpbbio.gpio as gpio
import serial
import re
import http.client
import urllib
import threading
import queue
import sys
import datetime
import time
import socket
import Adafruit_BMP.BMP085 as BMP085

altitude_in_meters = 112
phant_url = 'data.sparkfun.com'
phant_public_key = 'WGG8ONW8bMf7x2ad0WOY'
pressure_samples = []

pressure_sampling_lock = threading.Lock()
queue = queue.Queue()

uart = gpio.uarts.uart1
uart.open()

# We have a quarter-second timeout because if we start reading in
# the middle of a serial message or if a byte is dropped for any
# reason, we'll throw away the partial message and try again
ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600, timeout=0.25) 

pressure_sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

headers = {
	"Phant-Private-Key": str(sys.argv[1]),
	'Content-Type': 'application/x-www-form-urlencoded'
}

def sendData():
	while True:
		body = queue.get()

		success = False
		while not success:
			try:
				phantServer = http.client.HTTPConnection(phant_url)
				phantServer.request(method="POST", url="/input/" + phant_public_key, body=body, headers=headers)
				response = phantServer.getresponse()
				response.read()

				if response.status == 200:
					success = True
					print("Logged to server: " + body)
				else:
					print("Phant server returned status " + str(response.status) + ": " + response.reason)
			except (http.client.HTTPException, socket.error) as err:
				print("HTTP error: {0}".format(err))

			if not success:
				time.sleep(5)
				print("Retrying...")

def oncePerMinute():
	global next_interval_time
	while True:
		# Sleep for the remainder of the time until the next
		# interval, prevents timer drift
		next_interval_time += 60
		sleep_time = next_interval_time - time.time()
		time.sleep(sleep_time)

		device_time = str(datetime.datetime.now())
		current_cpm = cpm

		pressure = getPressure()
		sea_level_pressure = pressure / pow(1.0 - altitude_in_meters / 44330.0, 5.255)

		body = urllib.parse.urlencode({'cpm': current_cpm, 'device_time': device_time, 'pressure': '{0:0.2f}'.format(pressure), 'sea_level_pressure': '{0:0.2f}'.format(sea_level_pressure)})
		queue.put_nowait(body)

def samplePressure():
	global pressure_samples
	while True:
		with pressure_sampling_lock:
			pressure_samples.append(pressure_sensor.read_pressure())

def getPressure():
	global pressure_samples
	with pressure_sampling_lock:
		median_pressure = median(pressure_samples)
		pressure_samples = []
	return median_pressure

def median(number_list):
	sorted_list = sorted(number_list)
	length = len(sorted_list)
	if not length % 2:
		return (sorted_list[length // 2] + sorted_list[length // 2 - 1]) / 2.0
	else:
		return sorted_list[length // 2]

sendThread = threading.Thread(target = sendData)
sendThread.daemon = True
sendThread.start()

next_interval_time = time.time()

sampleThread = threading.Thread(target = oncePerMinute)
sampleThread.daemon = True
sampleThread.start()

pressureThread = threading.Thread(target = samplePressure)
pressureThread.daemon = True
pressureThread.start()

while True:
	bytes = ser.read(36)

	if len(bytes) == 36:
		try:
			line1 = bytes[2:18].decode('ascii')
			line2 = bytes[20:36].decode('ascii')
			#print(line1 + "  " + line2)

			cpm = int(re.search(r'CPM:\s*(\d+)', line1).group(1))
		except (UnicodeDecodeError):
			print("Unicode decoding error!")
