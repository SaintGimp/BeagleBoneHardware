from gimpbbio import gpio
from . import fake_filesystem

def test_pins_are_accessible_via_key():
	assert gpio.pins["USR0"].name == "USR0"

def test_pins_are_accessible_via_attribute():
	assert gpio.pins.usr0.name == "USR0"

def test_can_open_for_output(monkeypatch):
	fake_filesystem.hook(monkeypatch)

	gpio.pins.p8_15.open_for_output()

	export = fake_filesystem.get("/sys/class/gpio/export")
	assert export.content == "47"

	direction = fake_filesystem.get("/sys/class/gpio/gpio47/direction")
	assert direction.content == "out"

def test_can_set_output_pin_value_high(monkeypatch):
	fake_filesystem.hook(monkeypatch)

	gpio.pins.p8_15.open_for_output()
	gpio.pins.p8_15.set_high()

	export = fake_filesystem.get("/sys/class/gpio/gpio47/value")
	assert export.content == "1"

def test_can_set_output_pin_value_low(monkeypatch):
	fake_filesystem.hook(monkeypatch)

	gpio.pins.p8_15.open_for_output()
	gpio.pins.p8_15.set_low()

	export = fake_filesystem.get("/sys/class/gpio/gpio47/value")
	assert export.content == "0"

def test_can_open_for_input(monkeypatch):
	fake_filesystem.hook(monkeypatch)

	gpio.pins.p8_15.open_for_input()

	export = fake_filesystem.get("/sys/class/gpio/export")
	assert export.content == "47"

	direction = fake_filesystem.get("/sys/class/gpio/gpio47/direction")
	assert direction.content == "in"

def test_can_tell_if_pin_is_high(monkeypatch):
	fake_filesystem.hook(monkeypatch)
	value = fake_filesystem.get("/sys/class/gpio/gpio47/value")
	value.content = "1"

	assert gpio.pins.p8_15.is_high()
	assert not gpio.pins.p8_15.is_low()

def test_can_tell_if_pin_is_low(monkeypatch):
	fake_filesystem.hook(monkeypatch)
	value = fake_filesystem.get("/sys/class/gpio/gpio47/value")
	value.content = "0"

	assert gpio.pins.p8_15.is_low()
	assert not gpio.pins.p8_15.is_high()
