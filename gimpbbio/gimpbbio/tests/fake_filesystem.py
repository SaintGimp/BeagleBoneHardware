from gimpbbio import gpio

_files = {}
_next_available_file_descriptor = 1

def get_file_descriptor():
    global _next_available_file_descriptor
    fd = _next_available_file_descriptor
    _next_available_file_descriptor += 1
    return fd

class FakeFile:
    def __init__(self, name):
        self.name = name
        self.opened_mode = None
        self.has_been_read = False
        self.content = None

    def open(self, mode):
        self.has_been_read = False
        self.opened_mode = mode

    def write(self, text):
        self.content = text

    def read(self):
        if not self.has_been_read:
            self.has_been_read = True
            return self.content
        else:
            return ""

    def seek(self, position):
        if position == 0:
            self.has_been_read = False

    def close(self):
        self.opened_mode = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

def open(name, mode='r'):
    file = get(name)
    file.open(mode)
    file.file_descriptor = 0
    return file

def os_open(name, mode):
    file = get(name)
    file.open(mode)
    file.file_descriptor = get_file_descriptor()
    return file.file_descriptor

def os_close(file_descriptor):
    file = get_by_descriptor(file_descriptor)
    file.close()

def gpio_read(file_descriptor):
    file = get_by_descriptor(file_descriptor)
    return file.content

def gpio_write(file_descriptor, value):
    file = get_by_descriptor(file_descriptor)
    file.content = value

def hook(monkeypatch):
    monkeypatch.setattr('builtins.open', open)
    gpio.Pin._gpio_read_function = gpio_read
    gpio.Pin._gpio_write_function = gpio_write
    gpio.Pin._os_open_function = os_open
    gpio.Pin._os_close_function = os_close
    _files.clear()

def get(name):
    if name not in _files:
        _files[name] = FakeFile(name)

    return _files[name]

def get_by_descriptor(file_descriptor):
    return next(filter(lambda file: file.file_descriptor == file_descriptor, _files.values()))