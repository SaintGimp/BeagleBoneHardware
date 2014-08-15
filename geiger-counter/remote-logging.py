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

queue = queue.Queue()

uart = gpio.uarts.uart1
uart.open()

# We have a quarter-second timeout because if we start reading in
# the middle of a serial message or if a byte is dropped for any
# reason, we'll throw away the partial message and try again
ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600, timeout=0.25) 

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
				phantServer = http.client.HTTPConnection("phant.saintgimp.org")
				phantServer.request(method="POST", url="/input/3K2oGxKqelCo0ry50Ln4fpr1q7m", body=body, headers=headers)
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

		body = urllib.parse.urlencode({'CPM': cpm, 'Device_Time': str(datetime.datetime.now())})
		queue.put_nowait(body)

sendThread = threading.Thread(target = sendData)
sendThread.daemon = True
sendThread.start()

next_interval_time = time.time()

sampleThread = threading.Thread(target = oncePerMinute)
sampleThread.daemon = True
sampleThread.start()

while True:
	bytes = ser.read(36)

	if len(bytes) == 36:
		line1 = bytes[2:18].decode('ascii')
		line2 = bytes[20:36].decode('ascii')
		print(line1 + "  " + line2)

		cpm = int(re.search(r'CPM:\s*(\d+)', line1).group(1))
