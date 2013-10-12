_files = {}

class FakeFile:
    def __init__(self, name):
        self.name = name
        self.opened_mode = None
        self.has_been_read = False

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
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

def open(name, mode='r'):
    file = get(name)
    file.open(mode)
    return file

def hook(monkeypatch):
    monkeypatch.setattr('builtins.open', open)
    _files.clear()

def get(name):
    if name not in _files:
        _files[name] = FakeFile(name)

    return _files[name]

