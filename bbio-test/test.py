import gimpbbio.gpio as gpio
import gimpbbio.devices as devices
import time

def setup_led(pin):
	pin.open_for_output()
	pin.set_low()
	return pin

def setup_switch(pin):
	pin.open_for_input(pull = gpio.PULL_UP, active_state = gpio.ACTIVE_LOW)
	switch = devices.Switch(pin)
	switch.watch(on_press, on_release)
	return switch

def on_press(switch):
	leds_by_switch[switch].set_high()

def on_release(switch):
	leds_by_switch[switch].set_low()

red_led = setup_led(gpio.pins.p8_17)
green_led = setup_led(gpio.pins.p8_15)
yellow_led = setup_led(gpio.pins.p8_13)
blue_led = setup_led(gpio.pins.p8_11)

red_switch = setup_switch(gpio.pins.p8_18)
green_switch = setup_switch(gpio.pins.p8_16)
yellow_switch = setup_switch(gpio.pins.p8_14)
blue_switch = setup_switch(gpio.pins.p8_12)

leds = [red_led, green_led, yellow_led, blue_led]
leds_by_switch = {red_switch: red_led, green_switch: green_led, yellow_switch: yellow_led, blue_switch: blue_led}

# for x in range(20):
# 	for led in leds:
# 		led.set_high()
# 		time.sleep(.05)
# 		led.set_low()

time.sleep(1000)
