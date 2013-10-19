from .pin_definitions import _pin_definitions
from . import _gpio
import os
import errno

class Pin:
    _gpio_read_function = _gpio.read
    _gpio_write_function = _gpio.write
    _os_open_function = os.open
    _os_close_function = os.close

    def __init__(self):
        self.value_file_descriptor = None

    def open_for_input(self):
        self._open("in")

    def open_for_output(self):
        self._open("out")

    # We have a minor bit of duplication below in the interest of reducing
    # nested function calls for performance

    def is_high(self):
        return Pin._gpio_read_function(self.value_file_descriptor) == 1

    def is_low(self):
        return Pin._gpio_read_function(self.value_file_descriptor) == 0

    def set_high(self):
        Pin._gpio_write_function(self.value_file_descriptor, True)

    def set_low(self):
        Pin._gpio_write_function(self.value_file_descriptor, False)

    def close(self):
        Pin._os_close_function(self.value_file_descriptor)
        self._unexport()

    def _open(self, direction):
        self._export()
        self._set_direction(direction)

        value_filename = "/sys/class/gpio/gpio" + str(self.gpio) + "/value"
        self.value_file_descriptor = Pin._os_open_function(value_filename, os.O_RDWR)

    def _export(self):
        try:
            self._write("/sys/class/gpio/export", str(self.gpio))
        except OSError as e:
            # errno.EBUSY means the pin is already exported, which is fine
            if e.errno != errno.EBUSY:
                raise

    def _unexport(self):
        self._write("/sys/class/gpio/unexport", str(self.gpio))

    def _set_direction(self, direction):
        self._write("/sys/class/gpio/gpio" + str(self.gpio) + "/direction", direction)

    def _read(self, file):
        with open(file, "r") as file:
            return file.read()

    def _write(self, file, text):
        with open(file, "w") as file:
            file.write(text)


class PinCollection:
    def __init__(self):
        self.pins = dict((definition["key"], self.build_pin(definition)) for definition in _pin_definitions)

        for key, value in self.pins.items():
            setattr(self, key.lower(), value)

    def __getitem__(self, key):
        return self.pins[key]

    def build_pin(self, definition):
        pin = Pin()
        for key, value in definition.items():
            setattr(pin, key, value)
        return pin

pins = PinCollection()