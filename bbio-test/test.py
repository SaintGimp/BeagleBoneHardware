import gimpbbio.gpio as gpio
import gimpbbio.devices as devices
import time
import random

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

red_led = setup_led(gpio.pins.p9_12)
green_led = setup_led(gpio.pins.p9_14)
yellow_led = setup_led(gpio.pins.p9_16)
blue_led = setup_led(gpio.pins.p9_18)

red_switch = setup_switch(gpio.pins.p9_11)
green_switch = setup_switch(gpio.pins.p9_13)
yellow_switch = setup_switch(gpio.pins.p9_15)
blue_switch = setup_switch(gpio.pins.p9_17)

leds = [red_led, green_led, yellow_led, blue_led]
leds_by_switch = {red_switch: red_led, green_switch: green_led, yellow_switch: yellow_led, blue_switch: blue_led}

def cycle_leds_left_to_right():
	for x in range(20):
		for led in leds:
			led.set_high()
			time.sleep(.05)
			led.set_low()

def randomly_flash_leds():
	last_led = None
	for x in range(80):
		while True:
			led = random.choice(leds)
			if led != last_led:
				break

		led.set_high()
		time.sleep(.05)
		led.set_low()

		last_led = led

cycle_leds_left_to_right()
randomly_flash_leds()

time.sleep(1000)
