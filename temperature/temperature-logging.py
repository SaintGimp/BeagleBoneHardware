import Adafruit_BBIO.ADC as ADC
import time, datetime

sensor_pin = 'P9_40'
 
ADC.setup()

header = "timestamp, temp" 
print header
data_file = open("/var/tmp/temperature_data.txt", "w+")
data_file.write(header + '\n')

while True:
    timestamp = datetime.datetime.now()
    
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800  # 1.8V reference = 1800 mV
    temp_c = (millivolts - 500) / 10
    temp_f = (temp_c * 9/5) + 32

    data = str(timestamp) + ", " + str(temp_f)
    print data

    data_file.write(data + '\n')

    time.sleep(15)
