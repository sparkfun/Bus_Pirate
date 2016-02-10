#!/usr/bin/env python
# encoding: utf-8
"""
Example code to interface the Bus Pirate in binary mode
Highly based on https://github.com/themadinventor/esptool/blob/master/esptool.py
Brent Wilkins 2016

This code requires pyserial:
    $ sudo pip install pyserial
or:
    $ sudo easy_install -U pyserial
"""
import sys
import serial
import argparse

commands = {
        'BBIO1': '\x00',    # Enter reset binary mode
        'SPI1':  '\x01',    # Enter binary SPI mode
        'I2C1':  '\x02',    # Enter binary I2C mode
        'ART1':  '\x03',    # Enter binary UART mode
        '1W01':  '\x04',    # Enter binary 1-Wire mode
        'RAW1':  '\x05',    # Enter binary raw-wire mode
        'RESET': '\x0F',    # Reset Bus Pirate
        'STEST': '\x10',    # Bus Pirate self-tests
}

def arg_auto_int(x):
    return int(x, 0)

class FatalError(RuntimeError):
    """
    Wrapper class for runtime errors that aren't caused by internal bugs, but by
    Bus Pirate responses or input content.
    """
    def __init__(self, message):
        RuntimeError.__init__(self, message)

    @staticmethod
    def WithResult(message, result):
        """
        Return a fatal error object that includes the hex values of
        'result' as a string formatted argument.
        """
        return FatalError(message %  ', '.join(hex(ord(x)) for x in result))


def main():
    parser = argparse.ArgumentParser(description = 'Bus Pirate binary interface demo', prog = 'binaryModeDemo')

    parser.add_argument(
            '--port', '-p',
            help = 'Serial port device',
            default = '/dev/ttyUSB0')

    parser.add_argument(
            '--baud', '-b',
            help = 'Serial port baud rate',
            type = arg_auto_int,
            default = 115200)

    args = parser.parse_args()

    print '\nTrying port: ', args.port, ' at baudrate: ', args.baud

    try:
        port = serial.Serial(args.port, args.baud, timeout=0.1)
    except serial.serialutil.SerialException as e:
        print 'I/O error({0}): {1}'.format(e.errno, e.strerror)
        print 'Port cannot be opened'
    else:
        print 'Ready!'
        print 'Entering binary mode...\n'

        count = 0
        done = False
        while count < 20 and not done:
            count += 1
            port.write(commands.get('BBIO1'))
            #port.write('\x00')
            got = port.read(5)  # Read up to 5 bytes
            #print ':'.join('{:02x}'.format(ord(c)) for c in got)
            if got == 'BBIO1':
                done = True
        if not done:
            port.close()
            raise FatalError('Failed to enter binary mode')

        # Now that the Buspirate is in binary mode, choose a BP mode
        port.write(commands.get('RESET'))
        while True:
            got = port.readline()
            if not got:
                break
            print(got),

        """
        port.write(commands.get('SPI1'))
        got = port.read(4)
        if got == 'SPI1':
            print 'Entered binary SPI mode'
        else:
            raise FatalError('Buspirate failed to enter new mode')
        """

        port.close()

    #raise FatalError('Non-error')


if __name__ == '__main__':
    try:
        main()
    except FatalError as e:
        print '\nA fatal error occurred: %s' % e
        sys.exit(2)
