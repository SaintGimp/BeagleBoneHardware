import Adafruit_BBIO.GPIO as GPIO
import time
import datetime

count = 0
data_file = open("/var/tmp/test_data.txt", "w+")

def callback(pin):
	data_file.write(str(datetime.datetime.now()) + '\n')
	global count
	count += 1


input_pin = "P8_8"
GPIO.setup(input_pin, GPIO.IN)
GPIO.add_event_detect(input_pin, GPIO.RISING, callback=callback)

while True:
	count = 0
	time.sleep(1)
	print str(count) + " hz"