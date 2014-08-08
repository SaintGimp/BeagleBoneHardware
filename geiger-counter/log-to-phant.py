# coding: utf-8

import gimpbbio.gpio as gpio
import threading, time, datetime, signal
import Queue as queue

# http://stackoverflow.com/questions/9310350/twisted-non-blocking-method-how-to
# http://twistedmatrix.com/documents/current/web/howto/client.html
# http://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python


class GeigerCounterDataCollector:
	def __init__(self):
		self.count_accumulator = 0
		self.counts = [0] * 10
		self.count_index = 0
		self.counts_per_second = 0
		self.counts_per_minute = 0
		self.total_counts = 0
		self.elapsed_seconds = 0
		self.highest_cpm = 0
		self.next_collection_call = time.time()
		# Well-known conversion factor from the tube manufacturer
		self.conversion_factor = 0.0057
		self.queue = queue.Queue()
		self.quit_event = threading.Event()

	def start(self, input_pin):
		self.input_pin = input_pin
		self.input_pin.open_for_input()
		self.input_pin.watch(gpio.RISING, self.receive_data)
		
		thread = threading.Thread(target = self.once_per_second)
		thread.daemon = True
		thread.start()

		self.process_data()

	def stop(self):
		self.input_pin.close()
		self.quit_event.set()
		time.sleep(0.1)


	def receive_data(self, pin):
		self.queue.put_nowait(datetime.datetime.now())

	def process_data(self):
		while not self.quit_event.isSet():
			timestamp = self.queue.get()
			if not self.quit_event.isSet():
				self.count_accumulator += 1
				#self.data_file.write(str(timestamp) + '\n')
				# Send to remote server

	def once_per_second(self):
		while not self.quit_event.isSet():
			self.collect_data()
			self.print_statistics()

			# Schedule the next call for 1 second from the last one, prevents timer drift
			self.next_collection_call += 1
			self.quit_event.wait(self.next_collection_call - time.time())

	def collect_data(self):
		self.elapsed_seconds += 1

		# Decrement CPM with expired data from a minute ago
		self.counts_per_minute -= self.counts[self.count_index]

		# Store new data
		# Race condition here
		self.counts[self.count_index] = self.count_accumulator
		self.count_accumulator = 0

		# Increment CPM with new data
		self.counts_per_second = self.counts[self.count_index]
		self.counts_per_minute += self.counts[self.count_index]

		self.total_counts += self.counts[self.count_index]
		if self.counts_per_minute > self.highest_cpm:
			self.highest_cpm = self.counts_per_minute

		self.count_index += 1
		if self.count_index > 59:
			self.count_index = 0

	def print_statistics(self):
		micro_sieverts_per_hour = self.counts_per_minute * self.conversion_factor
		average_cpm = self.total_counts * 1.0 / self.elapsed_seconds * 60
		print("CPS: {0}, rolling CPM: {1}, avg CPM: {2:.1f}, max CPM: {3}, μSv/hr: {4:.2f}".format(self.counts_per_second, self.counts_per_minute, average_cpm, self.highest_cpm, micro_sieverts_per_hour))

def signal_handler(signal, frame):
    print('Exiting.')
    collector.stop()

signal.signal(signal.SIGINT, signal_handler)

collector = GeigerCounterDataCollector()
collector.start(gpio.pins.p8_8)
