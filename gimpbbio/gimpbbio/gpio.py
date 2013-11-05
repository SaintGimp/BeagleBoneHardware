from .pin_definitions import _pin_definitions
from . import _device_tree
from . import _gpio
import os
import errno
import select
import threading
import queue

PULL_DOWN = 0
PULL_UP = 1
ACTIVE_LOW = 1
ACTIVE_HIGH = 0
RISING = "rising"
FALLING = "falling"
BOTH = "both"

def _ensure_watcher_threads_are_running():
    global _epoll
    if _epoll is None:
        _epoll = select.epoll()
        _watcher_thread.start()
        _notifier_thread.start()

def _add_watch(pin):
    _watched_pins[pin.value_file_descriptor] = pin
    _epoll.register(pin.value_file_descriptor, select.EPOLLIN | select.EPOLLPRI | select.EPOLLET)

def _remove_watch(pin):
    _epoll.unregister(pin.value_file_descriptor)
    del _watched_pins[pin.value_file_descriptor]

# The underlying device tree is not buffered so any events that
# occur while we're busy processing a previous one might be lost.
# To prevent that, we buffer the events into a queue on the poll
# thread and invoke the callback from another thread. Note that
# specifying an edge trigger of BOTH will capture the state of the
# pin at some point after the trigger and it might have changed.
def _watcher():
    put_function = _event_queue.put_nowait

    while True:
        try:
            while True:
                events = _epoll.poll()

                for file_descriptor, event in events:
                    pin = _watched_pins[file_descriptor]
                    
                    if pin.edge_trigger == RISING:
                        put_function((pin, True))
                    elif pin.edge_trigger == FALLING:
                        put_function((pin, False))
                    else:
                        put_function((pin, pin.is_high()))
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            else:
                raise

def _notifier():
    while True:
        pin, is_high = _event_queue.get()

        if pin.is_new_watch:
            pin.is_new_watch = False
            continue

        pin.watch_callback(pin, is_high)

_epoll = None
_event_queue = queue.Queue()
_watched_pins = {}
_watcher_thread = threading.Thread(target = _watcher, daemon = True)
_notifier_thread = threading.Thread(target = _notifier, daemon = True)

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
