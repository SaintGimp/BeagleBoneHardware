import Adafruit_BBIO.GPIO as GPIO
input_pin = "P8_16"

GPIO.setup(input_pin, GPIO.IN)
print GPIO.input(input_pin)

def read_a_bunch():
    for x in range(1000):
        GPIO.input(input_pin)

from timeit import Timer
t = Timer(lambda: read_a_bunch())
print(t.timeit(number=1))