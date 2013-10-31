import gimpbbio.gpio as gpio
import time
import math

count = 0

def buffered_callback(pin, is_high):
	#pin, is_high = event
	# print("Watcher triggered, is_high = " + str(is_high))
	# time.sleep(1)
	global count
	count += 1

def unbuffered_callback():
	global count
	count += 1

output_pin = gpio.pins.p8_15
output_pin.open_for_output()
output_pin.set_low()

input_pin = gpio.pins.p8_16
input_pin.open_for_input()
input_pin.watch(gpio.RISING, buffered_callback)
#input_pin.watch_unbuffered(gpio.RISING, unbuffered_callback)

for step in range(3,8):
	delay = 1 / math.pow(10, step)

	for x in range(1000):
		output_pin.set_high()
		time.sleep(delay)
		output_pin.set_low()
		time.sleep(delay)

	time.sleep(1)
	print("For delay = " + str(delay) + ", count = " + str(count))
	count = 0
