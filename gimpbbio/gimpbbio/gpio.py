from .pin_definitions import _pin_definitions
from . import _gpio
import os
import errno
import select
import threading

PULL_DOWN = "pullDown"
PULL_UP = "pullUp"
PULL_NONE = "pullNone"
ACTIVE_LOW = 1
ACTIVE_HIGH = 0
RISING = "rising"
FALLING = "falling"
BOTH = "both"

def _ensure_watcher_threads_are_running():
    global _epoll
    if _epoll is None:
        _epoll = select.epoll()
        _poll_thread.start()

def _add_watch(pin):
    _watched_pins[pin.value_file_descriptor] = pin
    _epoll.register(pin.value_file_descriptor, select.EPOLLIN | select.EPOLLPRI | select.EPOLLET)

def _remove_watch(pin):
    _epoll.unregister(pin.value_file_descriptor)
    del _watched_pins[pin.value_file_descriptor]

# Note that specifying an edge trigger of BOTH will capture the
# state of the pin at some point after the trigger and it might
# have changed. RISING and FALLING triggers will always reliably
# report the state of the pin (since we don't have to read it)
def _poll_thread_function():
    while True:
        try:
            while True:
                events = _epoll.poll()

                for file_descriptor, event in events:
                    pin = _watched_pins[file_descriptor]
                    
                    if pin.is_new_watch:
                        pin.is_new_watch = False
                        continue

                    if pin.edge_trigger == RISING:
                        pin.watch_callback((pin, True))
                    elif pin.edge_trigger == FALLING:
                        pin.watch_callback((pin, False))
                    else:
                        pin.watch_callback((pin, _gpio.read(file_descriptor)))
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            else:
                raise

_epoll = None 
_watched_pins = {}
_poll_thread = threading.Thread(target = _poll_thread_function, daemon = True)

class Pin:
    _gpio_read_function = _gpio.read
    _gpio_write_function = _gpio.write
    _os_open_function = os.open
    _os_close_function = os.close

    def __init__(self):
        self.value_file_descriptor = None

    def open_for_input(self, pull = PULL_DOWN, active_state = ACTIVE_HIGH):
        self._set_pin_mux("input", pull)
        self._open("in")

        if active_state == ACTIVE_LOW:
            self._set_active_low("1")
        else:
            self._set_active_low("0")

    def open_for_output(self):
        self._set_pin_mux("output", PULL_DOWN)
        self._open("out")

    # We have a minor bit of duplication below in the interest of reducing
    # nested function calls for performance

    def is_high(self):
        return Pin._gpio_read_function(self.value_file_descriptor)

    def is_low(self):
        return Pin._gpio_read_function(self.value_file_descriptor)

    def set_high(self):
        Pin._gpio_write_function(self.value_file_descriptor, True)

    def set_low(self):
        Pin._gpio_write_function(self.value_file_descriptor, False)

    def close(self):
        Pin._os_close_function(self.value_file_descriptor)
        self._unexport()

    def watch(self, edge_trigger, callback):
        _ensure_watcher_threads_are_running()
        self.watch_callback = callback
        self.is_new_watch = True

        self.edge_trigger = edge_trigger
        edge_filename = "/sys/class/gpio/gpio" + str(self.gpio) + "/edge"
        self._write(edge_filename, edge_trigger)

        _add_watch(self)
    
    def unwatch(self):
        _remove_watch(self)

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
    
    def _set_pin_mux(self, direction, pull):
        overlay_name = "gimp-gpio-" + self.key
        self._load_device_tree_overlay(overlay_name)

        pin_state = direction + "_" + pull
        self._write_pin_state(pin_state)

    def _load_device_tree_overlay(self, overlay_name):
        # NOTE: once we load an overlay there's currently no good way to get rid of it.
        
        cape_manager = self._find_file_by_partial_match("/sys/devices", "bone_capemgr.")
        cape_slots_path = cape_manager + "/slots"

        slots = self._read(cape_slots_path)
        if overlay_name not in slots:
            print(cape_slots_path)
            print(overlay_name)
            self._write(cape_slots_path, overlay_name)

        while True:
            slots = self._read(cape_slots_path)
            if overlay_name in slots:
                break

    def _write_pin_state(self, state):
        ocp_path = self._find_file_by_partial_match("/sys/devices", "ocp.")
        pin_path = self._find_file_by_partial_match(ocp_path, "gpio-" + self.key.replace("_", "."))
        self._write(pin_path + "/state", state)

class PinCollection:
    def __init__(self):
        self.pins = dict((definition["key"], self.build_pin(definition)) for definition in _pin_definitions if "gpio" in definition)

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
