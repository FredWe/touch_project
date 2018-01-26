import subprocess
import serial
import re
import json

CMD_USBADDR = 'ls /dev/ttyUSB*'
CMD_LEDTEST = 'LedTest\n'
SAMPLE_INTERNAL = 0.01
CMD_GETDATA = 'StartGetTouchData %.2f\n' % SAMPLE_INTERNAL
BAUDRATE = 1500000
CONFIG_FILENAME = 'config_serial.json'

def get_usbpath():
    usbaddr = ''
    with subprocess.Popen(CMD_USBADDR, stdout=subprocess.PIPE, shell=True) as proc:
	    usbaddr = proc.stdout.readline().decode().strip()
    return usbaddr

def config_by_serial(usbpath):
    state_init, state_idle, state_ledon, state_sendingdata = range(4)
    with serial.Serial(usbpath, baudrate=BAUDRATE, timeout=0.1) as ser:
        state = state_init
        while state != state_idle:
            ser.write(b'\n')
            retline = ser.readline().decode().strip()
            if re.search(r'root@', retline):
                state = state_idle
        ser.write(CMD_LEDTEST.encode())
        state = state_ledon
        while state != state_idle:
            ser.write(b'\n')
            retline = ser.readline().decode().strip()
            if re.search(r'root@', retline):
                state = state_idle
        ser.write(CMD_GETDATA.encode())

def main():
    usbpath = get_usbpath()
    config_by_serial(usbpath)
    with open(CONFIG_FILENAME, 'w') as fp:
        json.dump({
            'SERIAL_PATH': usbpath,
            'BAUDRATE': BAUDRATE}, fp)

if __name__ == '__main__':
    main()
