import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, Extension, find_packages

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Home Automation',
               'Topic :: System :: Hardware']

setup(name             = 'gimpbbio',
      version          = '0.0.1',
      author           = 'Eric Lee',
      author_email     = 'saintgimp@hotmail.com',
      description      = 'A package for controlling BeagleBone IO channels',
      long_description = ' ', # open('README.md').read(),
      license          = 'MIT',
      keywords         = 'BeagleBone IO GPIO PWM ADC',
      url              = 'https://github.com/SaintGimp/BeagleBoneHardware',
      classifiers      = classifiers,
      packages         = find_packages(),
      #py_modules       = ['Gimp_I2C'],
      ext_modules      = [Extension('gimpbbio._gpio', ['gimpbbio/_gpio.c'])])
