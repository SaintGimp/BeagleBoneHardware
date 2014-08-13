import gimpbbio.gpio as gpio
import serial
import re
import http.client
import urllib
import threading
import queue
import sys
import datetime

queue = queue.Queue()

uart = gpio.uarts.uart1
uart.open()

# We have a quarter-second timeout because if we start reading in
# the middle of a serial message or if a byte is dropped for any
# reason, we'll throw away the partial message and try again
ser = serial.Serial(port = "/dev/ttyO1", baudrate=9600, timeout=0.25) 
phantServer = http.client.HTTPConnection("phant.saintgimp.org")

headers = {
	"Phant-Private-Key": str(sys.argv[1]),
	'Content-Type': 'application/x-www-form-urlencoded'
}

def sendData():
	while True:
		body = queue.get()
		phantServer.request(method="POST", url="/input/3K2oGxKqelCo0ry50Ln4fpr1q7m", body=body, headers=headers)
		response = phantServer.getresponse()
		response.read()

		# TODO: retry on transient errors
		if response.status == 200:
			print("Logged to server: " + body)
		else:
			print("Phant server returned status " + str(response.status) + ": " + response.reason)

thread = threading.Thread(target = sendData)
thread.daemon = True
thread.start()

number_of_updates = 0;

while True:
	bytes = ser.read(36)

	if len(bytes) == 36:
		number_of_updates += 1

		line1 = bytes[2:18].decode('ascii')
		line2 = bytes[20:36].decode('ascii')
		print(format(number_of_updates, '02d') + "| " + line1 + "  " + line2)

		# TODO: this relies on the geiger counter being fairly precise in its update
		# interval. We'll probably want to calculate minute intervals in this script
		# instead.
		if number_of_updates == 60:
			cpm = int(re.search(r'CPM:\s*(\d+)', line1).group(1))

			body = urllib.parse.urlencode({'CPM': cpm, 'Device_Time': str(datetime.datetime.now())})
			queue.put_nowait(body)

			number_of_updates = 0

