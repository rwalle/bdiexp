import serial

import logging
logger = logging.getLogger(__name__)


class RelaySwitch:

    ser = None

    def __init__(self, addr):
        self.DEVICE_ADDR = addr

    def init(self):

        self.ser = serial.Serial(self.DEVICE_ADDR, 9600, timeout=2)
        
    def turn_on(self):

        logger.info("turn on device")

        try:
            self.ser.write(b'2\n')
        except NameError:
            print('Device not initialized!')
            raise
                
    def turn_off(self):

        logger.info("turn off device")

        try:
            self.ser.write(b'1\n')
        except NameError:
            print('Device not initialized!')
            raise

    def close(self):

        self.ser.close()
        self.ser = None
