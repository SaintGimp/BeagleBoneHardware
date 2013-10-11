import bbio.gpio as gpio
import os


input_pin = gpio.pins.p8_16
input_pin.open_for_input()
print(input_pin.is_high())

def read_a_bunch1():
    filename = "/sys/class/gpio/gpio" + str(input_pin.gpio) + "/value"
    value_file = open(filename, "r")
    for x in range(1000):
        value_file.seek(0)
        value_file.read()    

def read_a_bunch2():
    for x in range(1000):
        input_pin.is_high()

def read_a_bunch3():
    filename = "/sys/class/gpio/gpio" + str(input_pin.gpio) + "/value"
    value_file = os.open(filename, os.O_RDONLY)
    for x in range(1000):
        os.pread(value_file, 1, 0)

from timeit import Timer
t = Timer(lambda: read_a_bunch3())
print(t.timeit(number=1))