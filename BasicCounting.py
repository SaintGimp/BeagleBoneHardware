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
		self.total_counts = 0
		self.elapsed_seconds = 0
		self.highest_cpm = 0
		self.next_collection_call = time.time()
		# Well-known conversion factor from the tube manufacturer
		self.conversion_factor = 0.0057

	def start(self, input_pin):
		GPIO.setup(input_pin, GPIO.IN)
		GPIO.add_event_detect(input_pin, GPIO.RISING, callback=self.count)
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
		print "CPS: {0}, rolling CPM: {1}, avg CPM: {2:.1f}, max CPM: {3}, μSv/hr: {4:.2f}".format(self.counts_per_second, self.counts_per_minute, average_cpm, self.highest_cpm, micro_sieverts_per_hour)

collector = GeigerCounterDataCollector()
collector.start("P8_11")
