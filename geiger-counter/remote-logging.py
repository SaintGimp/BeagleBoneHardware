import gimpbbio.gpio as gpio
import serial
import re
import http.client
import urllib
import threading
import queue
import sys

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
		phantServer.request(method="POST", url="/input/BD8mwo8ZMdU73kZP7MXAcK7oaJR", body=body, headers=headers)
		response = phantServer.getresponse()
		response.read()

		if response.status != 200:
			print("Phant server returned status " + str(response.status) + ": " + response.reason)

thread = threading.Thread(target = sendData)
thread.daemon = True
thread.start()

while True:
	bytes = ser.read(36)

	if len(bytes) == 36:
		line1 = bytes[2:18].decode('ascii')
		line2 = bytes[20:36].decode('ascii')
		print(line1)
		print(line2)

		cpm = int(re.search(r'CPM:\s*(\d+)', line1).group(1))
		cps = int(re.search(r'CPS:\s*(\d+)', line1).group(1))
		usph = float(re.search(r'uSv/hr:\s*(\d+\.\d+)', line2).group(1))

		body = urllib.parse.urlencode({'CPS': cps, 'CPM': cpm, 'uSv_Hr': usph})
		queue.put_nowait(body)

