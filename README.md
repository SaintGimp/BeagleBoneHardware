BeagleBone Black and Embedded Device Scripts
=============

This is a random collection of scripts for playing around with the BeagleBone Black and other embedded devices.  This code is guarenteed to be sloppy and is probably of use only to me.

**Prerequisites**

Install [Adafruit's BeagleBone IO Python Library](https://github.com/adafruit/adafruit-beaglebone-io-python)
on your BeagleBone.

**Geiger Counter Data Collection**

Scripts in the GeigerCounter folder are for collecting geiger counter data on a BeagleBone Black.  Wire the pulse output header of your geiger counter to a GPIO pin and to a ground
pin on your BBB.  Make sure the pulse output is 3.3V max!  I'm using the excellent [MightyOhm kit](http://mightyohm.com/blog/products/geiger-counter/). It's easy to use
as either a standalone device or a sensor for the BBB.  
