import gimpbbio.gpio as gpio
import gimpbbio.devices as devices
import time
import math
import datetime

count = 0

output_pin = gpio.pins.p8_15
output_pin.open_for_output()
output_pin.set_low()

def on_press(pin):
	output_pin.set_high()

def on_release(pin):
	output_pin.set_low()

input_pin = gpio.pins.p8_16
input_pin.open_for_input(pull = gpio.PULL_UP, active_state = gpio.ACTIVE_LOW)
switch = devices.Switch(input_pin)
switch.watch(on_press, on_release)

time.sleep(1000)
