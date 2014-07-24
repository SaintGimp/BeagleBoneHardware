import Adafruit_BBIO.GPIO as GPIO
import time, datetime

header = "timestamp" 
print header
data_file = open("/var/tmp/breakbeam_data.txt", "w+")
data_file.write(header + '\n')

sensor_pin = 'P9_11' 
GPIO.setup(sensor_pin, GPIO.IN)

while True:
  GPIO.wait_for_edge(sensor_pin, GPIO.RISING)

  timestamp = datetime.datetime.now()
  data = str(timestamp)

  print data
  data_file.write(data + '\n')
  data_file.flush()

