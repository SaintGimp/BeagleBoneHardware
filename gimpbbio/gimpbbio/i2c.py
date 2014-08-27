import smbus
import logging

# Build smbus for Python3
# sudo apt-get install libi2c-dev     # install dependency
# wget http://ftp.de.debian.org/debian/pool/main/i/i2c-tools/i2c-tools_3.1.0.orig.tar.bz2     # download i2c-tools source
# tar xf i2c-tools_3.1.0.orig.tar.bz2
# cd i2c-tools-3.1.0/py-smbus
# mv smbusmodule.c smbusmodule.c.orig  # backup
# wget https://gist.githubusercontent.com/sebastianludwig/c648a9e06c0dc2264fbd/raw/f4e5c3eb0ea768f30c9d7c5aa6961331dab7228a/smbusmodule.c     # download patched (Python 3) source
# sudo python3 setup.py build
# sudo python3 setup.py install

# ===========================================================================
# Forked from https://github.com/adafruit/Adafruit_Python_GPIO
# ===========================================================================

def get_default_bus():
  return 1

class Device(object):
  """Class for communicating with an I2C device using the smbus library.
  Allows reading and writing 8-bit, 16-bit, and byte array values to registers
  on the device."""
  def __init__(self, address, busnum):
    """Create an instance of the I2C device at the specified address on the
    specified I2C bus number."""
    self._address = address
    self._bus = smbus.SMBus(busnum)
    self._logger = logging.getLogger('GimpBBIO.I2C.Device.Bus.{0}.Address.{1:#0X}' \
                .format(busnum, address))

  def writeRaw8(self, value):
    """Write an 8-bit value on the bus (without register)."""
    value = value & 0xFF
    self._bus.write_byte(self._address, value)
    self._logger.debug("Wrote 0x%02X",
           value)

  def write8(self, register, value):
    """Write an 8-bit value to the specified register."""
    value = value & 0xFF
    self._bus.write_byte_data(self._address, register, value)
    self._logger.debug("Wrote 0x%02X to register 0x%02X", 
           value, register)

  def write16(self, register, value):
    """Write a 16-bit value to the specified register."""
    value = value & 0xFFFF
    self._bus.write_word_data(self._address, register, value)
    self._logger.debug("Wrote 0x%04X to register pair 0x%02X, 0x%02X", 
           value, register, register+1)

  def writeList(self, register, data):
    """Write bytes to the specified register."""
    self._bus.write_i2c_block_data(self._address, register, data)
    self._logger.debug("Wrote to register 0x%02X: %s", 
           register, data)

  def readList(self, register, length):
    """Read a length number of bytes from the specified register.  Results 
    will be returned as a bytearray."""
    results = self._bus.read_i2c_block_data(self._address, register, length)
    self._logger.debug("Read the following from register 0x%02X: %s",
           register, results)
    return results

  def readRaw8(self):
    """Read an 8-bit value on the bus (without register)."""
    result = self._bus.read_byte(self._address) & 0xFF
    self._logger.debug("Read 0x%02X",
          result)
    return result

  def readU8(self, register):
    """Read an unsigned byte from the specified register."""
    result = self._bus.read_byte_data(self._address, register) & 0xFF
    self._logger.debug("Read 0x%02X from register 0x%02X",
           result, register)
    return result

  def readS8(self, register):
    """Read a signed byte from the specified register."""
    result = self.readU8(register)
    if result > 127: 
      result -= 256
    return result

  def readU16(self, register, little_endian=True):
    """Read an unsigned 16-bit value from the specified register, with the
    specified endianness (default little endian, or least significant byte
    first)."""
    result = self._bus.read_word_data(self._address,register) & 0xFFFF
    self._logger.debug("Read 0x%04X from register pair 0x%02X, 0x%02X",
               result, register, register+1)
    # Swap bytes if using big endian because read_word_data assumes little 
    # endian on ARM (little endian) systems.
    if not little_endian:
      result = ((result << 8) & 0xFF00) + (result >> 8)
    return result

  def readS16(self, register, little_endian=True):
    """Read a signed 16-bit value from the specified register, with the
    specified endianness (default little endian, or least significant byte
    first)."""
    result = self.readU16(register, little_endian)
    if result > 32767:
      result -= 65536
    return result

  def readU16LE(self, register):
    """Read an unsigned 16-bit value from the specified register, in little
    endian byte order."""
    return self.readU16(register, little_endian=True)

  def readU16BE(self, register):
    """Read an unsigned 16-bit value from the specified register, in big
    endian byte order."""
    return self.readU16(register, little_endian=False)

  def readS16LE(self, register):
    """Read a signed 16-bit value from the specified register, in little
    endian byte order."""
    return self.readS16(register, little_endian=True)

  def readS16BE(self, register):
    """Read a signed 16-bit value from the specified register, in big
    endian byte order."""
    return self.readS16(register, little_endian=False)