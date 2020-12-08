import time
import traceback

import serial
from serial.threaded import LineReader, ReaderThread


class PrintLines(LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        print('port opened\n')
        # self.write_line('hello world')

    def handle_line(self, data):
        print('line received: {}\n'.format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        print('port closed\n')

if __name__ == '__main__':
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=1)
    with ReaderThread(ser, PrintLines) as protocol:
        while True:
            message_to_send = input()
            time.sleep(1)
            protocol.write_line('AT+SEND={}'.format(str(len(message_to_send))))
            time.sleep(1)
            protocol.write_line(message_to_send)

            time.sleep(2)