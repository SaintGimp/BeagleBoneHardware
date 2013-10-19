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

    value_file = fake_filesystem.get("/sys/class/gpio/gpio47/value")
    assert value_file.content == True

def test_can_set_output_pin_value_low(monkeypatch):
    fake_filesystem.hook(monkeypatch)

    gpio.pins.p8_15.open_for_output()
    gpio.pins.p8_15.set_low()

    value_file = fake_filesystem.get("/sys/class/gpio/gpio47/value")
    assert value_file.content == False

def test_can_open_for_input(monkeypatch):
    fake_filesystem.hook(monkeypatch)

    gpio.pins.p8_15.open_for_input()

    export = fake_filesystem.get("/sys/class/gpio/export")
    assert export.content == "47"

    direction = fake_filesystem.get("/sys/class/gpio/gpio47/direction")
    assert direction.content == "in"

def test_can_tell_if_pin_is_high(monkeypatch):
    fake_filesystem.hook(monkeypatch)

    gpio.pins.p8_15.open_for_input()
    value_file = fake_filesystem.get("/sys/class/gpio/gpio47/value")
    value_file.content = True

    assert gpio.pins.p8_15.is_high()
    assert not gpio.pins.p8_15.is_low()

def test_can_tell_if_pin_is_low(monkeypatch):
    fake_filesystem.hook(monkeypatch)

    gpio.pins.p8_15.open_for_input()
    value_file = fake_filesystem.get("/sys/class/gpio/gpio47/value")
    value_file.content = False

    assert gpio.pins.p8_15.is_low()
    assert not gpio.pins.p8_15.is_high()

def test_can_close(monkeypatch):
    fake_filesystem.hook(monkeypatch)

    gpio.pins.p8_15.open_for_input()
    gpio.pins.p8_15.close()

    value_file = fake_filesystem.get("/sys/class/gpio/gpio47/value")
    value_file.opened_mode = None

    unexport_file = fake_filesystem.get("/sys/class/gpio/unexport")
    assert unexport_file.content == "47"
