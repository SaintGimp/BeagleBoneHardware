import gimpbbio.gpio as gpio
import gimpbbio.devices as devices
import time
import random
import threading
import seven_segment

sequence = []
input_enabled = False
next_expected_color = 0
game_over = threading.Event()

def setup_led(pin):
	pin.open_for_output()
	pin.set_low()
	return pin

def setup_switch(pin):
	pin.open_for_input(pull = gpio.PULL_UP, active_state = gpio.ACTIVE_LOW)
	switch = devices.Switch(pin)
	switch.watch(on_press, on_release)
	return switch

class Color:
	def __init__(self, led, switch):
		self.led = led
		self.switch = switch

		led.color = self
		switch.color = self

def play_beginning_of_game():
	for x in range(20):
		for color in colors:
			color.led.set_high()
			time.sleep(.05)
			color.led.set_low()
	time.sleep(2)

def play_end_of_game():
	for x in range(50):
		for color in colors:
			color.led.set_high()
		time.sleep(.04)
		for color in colors:
			color.led.set_low()
		time.sleep(.04)

def play_sequence():
	for color in sequence:
		color.led.set_high()
		time.sleep(.65)
		color.led.set_low()
		time.sleep(.5)

def setup_game():
	global next_expected_color
	global input_enabled
	global sequence

	input_enabled = False
	next_expected_color = 0
	sequence = [random.choice(colors)]

def on_press(switch):
	global input_enabled

	if input_enabled:
		switch.color.led.set_high()

		if switch.color != sequence[next_expected_color]:
			game_over.set()

def on_release(switch):
	global next_expected_color
	global input_enabled

	if input_enabled:
		switch.color.led.set_low()

		next_expected_color += 1

		if next_expected_color == len(sequence):
			input_enabled = False
			time.sleep(1)
			sequence.append(random.choice(colors))
			play_sequence()
			next_expected_color = 0
			input_enabled = True

red_led = setup_led(gpio.pins.p9_12)
green_led = setup_led(gpio.pins.p9_14)
yellow_led = setup_led(gpio.pins.p9_16)
blue_led = setup_led(gpio.pins.p9_18)

red_switch = setup_switch(gpio.pins.p9_11)
green_switch = setup_switch(gpio.pins.p9_13)
yellow_switch = setup_switch(gpio.pins.p9_15)
blue_switch = setup_switch(gpio.pins.p9_17)

red = Color(red_led, red_switch)
green = Color(green_led, green_switch)
yellow = Color(yellow_led, yellow_switch)
blue = Color(blue_led, blue_switch)

colors = [red, green, yellow, blue]

seven_segment.display_digit(0)

while True:
	setup_game()
	play_beginning_of_game()
	input_enabled = False
	play_sequence()
	input_enabled = True

	game_over.wait()

	input_enabled = False
	play_end_of_game()
	game_over.clear()
	time.sleep(2)

