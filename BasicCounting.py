# coding: utf-8

import Adafruit_BBIO.GPIO as GPIO
import threading, time

class GeigerCounterDataCollector:
	def __init__(self):
		self.count_accumulator = 0
		self.counts = [0] * 60
		self.count_index = 0
		self.counts_per_second = 0
		self.counts_per_minute = 0
		self.next_collection_call = time.time()
		# Well-known conversion factor from the tube manufacturer
		self.conversion_factor = 0.0057

	def start(self, input_pin):
		GPIO.setup("P8_14", GPIO.IN)
		GPIO.add_event_detect("P8_14", GPIO.RISING, callback=self.count)
		self.once_per_second()

	def count(self, channel):
		self.count_accumulator += 1

	def once_per_second(self):
		self.collect_data()
		self.print_statistics()

		# Schedule the next call for 1 second from the last one, prevents timer drift
		self.next_collection_call += 1
		threading.Timer(self.next_collection_call - time.time(), self.once_per_second).start()

	def collect_data(self):
		# Decrement CPM with expired data from a minute ago
		self.counts_per_minute -= self.counts[self.count_index]

		# Store new data
		# Race condition here
		self.counts[self.count_index] = self.count_accumulator
		self.count_accumulator = 0

		# Increment CPM with new data
		self.counts_per_second = self.counts[self.count_index]
		self.counts_per_minute += self.counts[self.count_index]

		self.count_index += 1
		if self.count_index > 59:
			self.count_index = 0

	def print_statistics(self):
		micro_sieverts_per_hour = self.counts_per_minute * self.conversion_factor
		print "CPS: {0}, CPM: {1}, μSv/hr: {2:.2f}".format(self.counts_per_second, self.counts_per_minute, micro_sieverts_per_hour)

collector = GeigerCounterDataCollector()
collector.start("P8_14")
