time:
	ntpdate -b -s -u pool.ntp.org

publish: clean
	python3 setup.py sdist upload

clean:
	rm -f *.pyo
	rm -f *.egg
	rm -f overlays/*.pyo overlays/*.pyc

tests:
	py.test

build:
	python3 setup.py build --force

dev:
	python3 setup.py develop

install: build
	python3 setup.py install --force
