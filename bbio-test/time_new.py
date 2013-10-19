import gimpbbio.gpio as gpio
import os
import time

input_pin = gpio.pins.p8_16
input_pin.open_for_input()
print(input_pin.is_high())

output_pin = gpio.pins.p8_15
output_pin.open_for_output()

def read_a_bunch1():
    filename = "/sys/class/gpio/gpio" + str(input_pin.gpio) + "/value"
    value_file = open(filename, "r")
    for x in range(1000):
        value_file.seek(0)
        value_file.read()    

def read_a_bunch2():
    func = input_pin.is_high
    for x in range(1000):
        func()

def read_a_bunch3():
    filename = "/sys/class/gpio/gpio" + str(input_pin.gpio) + "/value"
    value_file = os.open(filename, os.O_RDONLY)
    for x in range(1000):
        os.pread(value_file, 1, 0)

def write_a_bunch():
    high = output_pin.set_high
    low = output_pin.set_low
    for x in range(500):
        high()
        low()

from timeit import Timer
t = Timer(lambda: write_a_bunch())
print(t.timeit(number=1))