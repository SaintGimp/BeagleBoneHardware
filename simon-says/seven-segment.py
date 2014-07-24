import gimpbbio.gpio as gpio

pins = [gpio.pins.p9_21, gpio.pins.p9_22, gpio.pins.p9_23, gpio.pins.p9_24, gpio.pins.p9_25, gpio.pins.p9_26, gpio.pins.p9_27, gpio.pins.p9_28]
segments = [[pins[0], pins[1], pins[2], pins[3], pins[4], pins[5]],
           [pins[1], pins[2]]]

def display_digit(digit):
	for pin in pins:
		pin.set_high()

	for pin in segments[digit]:
		pin.set_low()
