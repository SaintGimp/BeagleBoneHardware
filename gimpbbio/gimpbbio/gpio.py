from .pin_definitions import _pin_definitions
from . import _device_tree
from . import _gpio
import os
import errno

PULLDOWN = 0
PULLUP = 1
ACTIVE_LOW = 1
ACTIVE_HIGH = 0

class Pin:
    _gpio_read_function = _gpio.read
    _gpio_write_function = _gpio.write
    _os_open_function = os.open
    _os_close_function = os.close

    def __init__(self):
        self.value_file_descriptor = None

    def open_for_input(self, pull = PULLDOWN, active_state = ACTIVE_HIGH):
        if pull == PULLUP:
            self._configure_device_tree_for_pullup()

        self._open("in")

        if active_state == ACTIVE_LOW:
            self._set_active_low("1")

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

    def _set_active_low(self, active_low):
        self._write("/sys/class/gpio/gpio" + str(self.gpio) + "/active_low", active_low)

    def _read(self, filename):
        with open(filename, "r") as file:
            return file.read()

    def _write(self, filename, text):
        with open(filename, "w") as file:
            file.write(text)

    def _find_file_by_partial_match(self, path, pattern):
        return path + "/" + next(item for item in os.listdir(path) if pattern in item)
    
    def _configure_device_tree_for_pullup(self):
        # We only need to apply a device tree overlay if we're setting
        # a pullup, otherwise the default is fine. Might want to expand
        # this in the future to support more options, or to support
        # runtime config changes ala https://github.com/nomel/beaglebone.git

        # NOTE: once we set an overlay there's no good way to get rid of
        # it.  You'll have to reboot to go back to pulldown on the pin.

        overlay_name = self._build_device_tree_overlay()
        self._load_device_tree_overlay(overlay_name)

    def _build_device_tree_overlay(self):
        data = 0x37
        overlay_name = "gimpbbio_" + self.key
        dts_filename = "/lib/firmware/" + overlay_name + "-00A0.dts"
        dtbo_filename = "/lib/firmware/" + overlay_name + "-00A0.dtbo"

        dts_text = _device_tree._template
        dts_text = dts_text.replace("___PIN_KEY___", self.key)
        dts_text = dts_text.replace("___PIN_DOT_KEY___", self.key.replace("_", '.'))
        dts_text = dts_text.replace("___PIN_FUNCTION___", self.options[data & 7])
        dts_text = dts_text.replace("___PIN_OFFSET___", self.muxRegOffset)
        dts_text = dts_text.replace("___DATA___", "0x%x" % data)

        self._write(dts_filename, dts_text)

        command = 'dtc -O dtb -o ' + dtbo_filename + ' -b 0 -@ ' + dts_filename;
        os.system(command);

        return overlay_name

    def _load_device_tree_overlay(self, overlay_name):
        cape_manager = self._find_file_by_partial_match("/sys/devices", "bone_capemgr.")
        cape_slots_path = cape_manager + "/slots"

        slots = self._read(cape_slots_path)
        if overlay_name not in slots:
            self._write(cape_slots_path, overlay_name)

        while True:
            slots = self._read(cape_slots_path)
            if overlay_name in slots:
                break

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