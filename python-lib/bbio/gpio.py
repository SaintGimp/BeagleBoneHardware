from .pin_definitions import _pin_definitions

IN = "in"
OUT = "out"
HIGH = "1"
LOW = "0"

class Pin:
    def __init__(self):
        self._value_file = None

    def open_for_input(self):
        self._open(IN)

    def open_for_output(self):
        self._open(OUT)

    def is_high(self):
        return self._get_value()[0] == "1"

    def is_low(self):
        return not self.is_high()

    def set_high(self):
        self._set_value(HIGH)

    def set_low(self):
        self._set_value(LOW)

    def close(self):
        self._unexport()

    def _open(self, direction):
        self._export()
        self._set_direction(direction)

    def _export(self):
        try:
            self._write("/sys/class/gpio/export", str(self.gpio))
        except OSError:
            # The pin is already exported
            pass

    def _unexport(self):
        self._write("/sys/class/gpio/export", str(self.gpio))

    def _set_direction(self, direction):
        self._write("/sys/class/gpio/gpio" + str(self.gpio) + "/direction", direction)

    def _get_value(self):
        return self._read("/sys/class/gpio/gpio" + str(self.gpio) + "/value")

    def _set_value(self, value):
        self._write("/sys/class/gpio/gpio" + str(self.gpio) + "/value", value)

    # TODO: this is simple but slow IO.  Performance problems become apparent in
    # tight loops.  Major speedup possibilities include:
    # - cache the file handle for the value file
    # - use os.pread to skip Python layers
    # - implement read in C (returning int) to skip allocation of result buffers

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