from . import gpio
import time
import datetime

# This wraps a pin and treats it as a mechanical switch that needs
# to be debounced. In order to do proper debouncing we need to watch
# for both rising and falling events, but those events might not
# accurately report the state of the pin. Instead we have to keep
# track of whether the switch is low or high ourselves. We also
# integrate over the changes to filter out bounce noise.
class Switch:
    def __init__(self, pin):
        self._pin = pin
        self.ignore_queued_changes_duration = datetime.timedelta(milliseconds = 3)
        self.last_debounce_time = datetime.datetime.min

    def watch(self, on_high = None, on_low = None):
        self._on_high = on_high
        self._on_low = on_low
        self._current_state = self._pin.is_high()
        
        self._pin.watch(gpio.BOTH, self._on_change)

    def _on_change(self, pin, is_high, timestamp):
        # While we were doing the last debounce integration we might have
        # got a couple more pin change events queued up so we ignore them
        # if they're old.
        if timestamp < self.last_debounce_time:
            return
        
        new_state = self._debounced_state(3, 30)
        if new_state != self._current_state:
            self._current_state = new_state

            if self._current_state and self._on_high:
                self._on_high(self)
            if not self._current_state and self._on_low:
                self._on_low(self)
        
        self.last_debounce_time = datetime.datetime.now()

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
