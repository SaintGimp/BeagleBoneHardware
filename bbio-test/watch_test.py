import gimpbbio.gpio as gpio
import time
import datetime

count = 0
data_file = open("/var/tmp/test_data.txt", "w+")

def callback(pin):
	data_file.write(str(datetime.datetime.now()) + '\n')
	global count
	count += 1

input_pin = gpio.pins.p8_8
input_pin.open_for_input()
input_pin.watch(gpio.RISING, callback)

while True:
	count = 0
	time.sleep(1)
	print(str(count) + " hz")
