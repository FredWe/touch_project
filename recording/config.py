import subprocess
import re
import json
import logging
import serial
import enum

CMD_USBADDR = 'ls /dev/ttyUSB*'
CMD_LEDTEST = 'LedTest\n'
SAMPLE_INTERNAL = 0.01
CMD_GETDATA = 'StartGetTouchData %.2f\n' % SAMPLE_INTERNAL
BAUDRATE = 1500000
CONFIG_FILENAME = 'config_serial.json'
BYTEN = 63

class Serstate(enum.Enum):
    STATE_INIT = 1
    STATE_IDLE = 2
    STATE_SENDING = 3
    STATE_EXIT = 0

def get_usbpath():
    usbaddr = ''
    with subprocess.Popen(CMD_USBADDR, stdout=subprocess.PIPE, shell=True) as proc:
        usbaddr = proc.stdout.readline().decode().strip()
    return usbaddr

def process_bystate(ser, currstate):
    ser.write(b'\n')
    retline = ser.readline().decode().strip()
    logging.debug(retline)
    if len(retline.split()) == 63:
        return Serstate.STATE_SENDING
    if currstate != Serstate.STATE_IDLE and re.search(r'root@', retline):
        return Serstate.STATE_IDLE
    if currstate == Serstate.STATE_IDLE:
        ser.write(CMD_LEDTEST.encode())
        ser.write(b'\n')
        ser.write(CMD_GETDATA.encode())
        return Serstate.STATE_EXIT
    if currstate == Serstate.STATE_SENDING:
        return Serstate.STATE_EXIT

def config_by_serial(usbpath):
    with serial.Serial(usbpath, baudrate=BAUDRATE, timeout=0.1) as ser:
        state = Serstate.STATE_INIT
        while state != Serstate.STATE_EXIT:
            state = process_bystate(ser, state)
            logging.debug(state)

def main():
    logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.WARN)
    usbpath = get_usbpath()
    config_by_serial(usbpath)
    with open(CONFIG_FILENAME, 'w') as fp:
        json.dump({
            'SERIAL_PATH': usbpath,
            'BAUDRATE': BAUDRATE}, fp)

if __name__ == '__main__':
    main()
