import gimpbbio.gpio as gpio
import time
import datetime
import threading
import queue

# The queued approach seems to capture slightly more events at low rates,
# but gets capped somewhere around 3.5k events per second. It might be
# more worthwhile for slower writing operations (like remote HTTP).

count = 0
data_file = open("/var/tmp/test_data.txt", "w+")
queue = queue.Queue()
	
def receive_data(pin):
	queue.put_nowait(datetime.datetime.now())

def once_per_second():
	global count
	while True:
		count = 0
		time.sleep(1)
		print(str(count) + " hz")
		print("Queue length: " + str(queue.qsize()))

input_pin = gpio.pins.p8_8
input_pin.open_for_input()
input_pin.watch(gpio.RISING, receive_data)

thread = threading.Thread(target = once_per_second)
thread.daemon = True
thread.start()

while True:
	timestamp = queue.get()
	count += 1
	data_file.write(str(timestamp) + '\n')
