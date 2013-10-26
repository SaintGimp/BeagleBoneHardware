import gimpbbio.gpio as gpio
import time

output_pin = gpio.pins.p8_16
output_pin.open_for_output()
output_pin.set_high()
time.sleep(1)
output_pin.set_low()

print("Testing input . . .")
input_pin = gpio.pins.p8_16
input_pin.open_for_input()
print(input_pin.is_high())

