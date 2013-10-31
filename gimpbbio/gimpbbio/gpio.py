from .pin_definitions import _pin_definitions
from . import _device_tree
from . import _gpio
import os
import errno
import select
import threading
import queue
import time

PULL_DOWN = 0
PULL_UP = 1
ACTIVE_LOW = 1
ACTIVE_HIGH = 0
RISING = "rising"
FALLING = "falling"
BOTH = "both"

class Pin:
    _gpio_read_function = _gpio.read
    _gpio_write_function = _gpio.write
    _os_open_function = os.open
    _os_close_function = os.close

    def __init__(self):
        self.value_file_descriptor = None

    def open_for_input(self, pull = PULL_DOWN, active_state = ACTIVE_HIGH):
        if pull == PULL_UP:
            self._configure_device_tree_for_pullup()

        self._open("in")

        if active_state == ACTIVE_LOW:
            self._set_active_low("1")
        else:
            self._set_active_low("0")

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

    # The underlying device tree is not buffered so any events that
    # occur while we're busy processing a previous one might be lost.
    # To prevent that, we buffer the events into a queue on the poll
    # thread and invoke the callback from another thread. Note that
    # specifying an edge trigger of BOTH will capture the state of the
    # pin at some point after the trigger and it might have changed.
    def watch(self, edge_trigger, callback):
        self.edge_trigger = edge_trigger
        self.event_queue = queue.Queue()
        self._watch_initialize(edge_trigger)

        watcher_thread = threading.Thread(target = self._watcher, daemon = True)
        watcher_thread.start()
        notifier_thread = threading.Thread(target = self._notifier, args = (callback,), daemon = True)
        notifier_thread.start()
    
    # Use this if you want event notifications as fast as possible
    def watch_unbuffered(self, edge_trigger, callback):
        self._watch_initialize(edge_trigger)

        watcher_thread = threading.Thread(target = self._unbuffered_watcher, args = (callback,), daemon = True)
        watcher_thread.start()

    def _watch_initialize(self, edge_trigger):
        edge_filename = "/sys/class/gpio/gpio" + str(self.gpio) + "/edge"
        self._write(edge_filename, edge_trigger)

        self.epoll = select.epoll()
        self.epoll.register(self.value_file_descriptor, select.EPOLLIN | select.EPOLLPRI | select.EPOLLET)
        # The first poll always returns immediately so we do one as a throw-away
        self.epoll.poll()
        
    def _watcher(self):
        put_function = self.event_queue.put_nowait

        while True:
            self.epoll.poll()

            if self.edge_trigger == RISING:
                put_function((self, True))
            elif self.edge_trigger == FALLING:
                put_function((self, False))
            else:
                put_function((self, self.is_high()))

    def _notifier(self, callback):
        while True:
            pin, is_high = self.event_queue.get()
            callback(pin, is_high)

    def _unbuffered_watcher(self, callback):
        while True:
            self.epoll.poll()
            callback()

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

# This wraps a pin and treats it as a mechanical switch that needs
# to be debounced. In order to do proper debouncing we need to watch
# for both rising and falling events, but those events might not
# accurately report the state of the pin. Instead we have to keep
# track of whether the switch is low or high ourselves. We also
# integrate over the changes to filter out bounce noise.
class Switch:
    def __init__(self, pin):
        self._pin = pin

    def watch(self, on_high = None, on_low = None):
        self._on_high = on_high
        self._on_low = on_low
        self._current_state = self._pin.is_high()
        
        self._pin.watch_unbuffered(BOTH, self._on_change)

    def _on_change(self):
        new_state = self._debounced_state(3, 30)
        if new_state != self._current_state:
            self._current_state = new_state

            if self._current_state and self._on_high:
                self._on_high(self._pin)
            if not self._current_state and self._on_low:
                self._on_low(self._pin)

    def _debounced_state(self, poll_interval_ms, debounce_time_ms):
        maximum = debounce_time_ms / poll_interval_ms
        integrator = maximum / 2.0

        while True:
            if self._pin.is_high():
                integrator += 1
            else:
                integrator -= 1

            if integrator <= 0:
                return False
            elif integrator >= maximum:
                return True
            
            time.sleep(poll_interval_ms / 1000)
