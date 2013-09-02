BeagleBone Black Geiger Counter Data Collection
=============

This is a random collection of code snippets for collecting geiger counter data on a BeagleBone Black.

**Prerequisites**

Install [Adafruit's BeagleBone IO Python Library](https://github.com/adafruit/adafruit-beaglebone-io-python)
on your BeagleBone.  Next wire the pulse output header of your geiger counter to a GPIO pin and to a ground
pin on your BBB.  Make sure the pulse output is 3.3V max!

**Geiger Counter Kit**
I'm using the excellent [MightyOhm kit](http://mightyohm.com/blog/products/geiger-counter/). It's easy to use
as either a standalone device or a sensor for the BBB.