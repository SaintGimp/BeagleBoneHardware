import gimpbbio.gpio as gpio

pins = [gpio.pins.p9_21, gpio.pins.p9_22, gpio.pins.p9_23, gpio.pins.p9_24, gpio.pins.p9_25, gpio.pins.p9_26, gpio.pins.p9_27, gpio.pins.p9_28]
segments = [[pins[0], pins[1], pins[2], pins[3], pins[4], pins[5]],         # 0
           [pins[1], pins[2]],                                              # 1
           [pins[0], pins[1], pins[3], pins[4], pins[6]],                   # 2
           [pins[0], pins[1], pins[2], pins[3], pins[6]],                   # 3
           [pins[1], pins[2], pins[5], pins[6]],                            # 4
           [pins[0], pins[2], pins[3], pins[5], pins[6]],                   # 5
           [pins[0], pins[2], pins[3], pins[4], pins[5], pins[6]],          # 6
           [pins[0], pins[1], pins[2]],                                     # 7
           [pins[0], pins[1], pins[2], pins[3], pins[4], pins[5], pins[6]], # 8
           [pins[0], pins[1], pins[2], pins[5], pins[6]]]                   # 9

for pin in pins:
	pin.open_for_output()

def display_digit(digit):
	for pin in pins:
		pin.set_high()

	for pin in segments[digit]:
		pin.set_low()
