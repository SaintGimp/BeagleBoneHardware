import gimpbbio.gpio as gpio
import time

print("Testing output . . .")
output_pin = gpio.pins.p8_15
output_pin.open_for_output()
output_pin.set_high()
time.sleep(1)
output_pin.set_low()

print("Testing input, press button . . .")
input_pin = gpio.pins.p8_16
input_pin.open_for_input(pull = gpio.PULLUP, active_state = gpio.ACTIVE_LOW)
while True:
	print(input_pin.is_high())
	time.sleep(.5)

