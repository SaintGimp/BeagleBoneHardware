import Adafruit_BBIO.GPIO as GPIO
import time
import math

count = 0

def callback(pin):
	global count
	count += 1


input_pin = "P8_8"
GPIO.setup(input_pin, GPIO.IN)
GPIO.add_event_detect(input_pin, GPIO.RISING, callback=callback)

while True:
	count = 0
	time.sleep(1)
	print str(count) + " hz"