import os
import time
import traceback

import serial
from serial.threaded import LineReader, ReaderThread

message_sended = True


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


class MessageReceiver(LineReader):

    def __init__(self, log_to_console=True):
        super().__init__()
        self.log_to_console = log_to_console

    def connection_made(self, transport):
        super(MessageReceiver, self).connection_made(transport)
        print('port opened\n')
        # self.write_line('hello world')

    def handle_line(self, data):
        # raw_response = repr(data)
        raw_response = data
        self.log(raw_response)
        if raw_response == 'AT,SENDED':
            global message_sended
            message_sended = True
        else:
            response_as_list = raw_response.split(',')
            if response_as_list[0] == 'LR':
                print('got message from {sender} with length {length}: {message}'.format(sender=response_as_list[1],
                                                                                         length=response_as_list[2],
                                                                                         message=response_as_list[3]))

    def log(self, msg):
        if self.log_to_console:
            print(msg)

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        print('port closed\n')


class Chatter:

    def __init__(self, serial_conn):
        self.serial_conn = serial_conn

    def start_chatting(self):
        with ReaderThread(self.serial_conn, MessageReceiver) as protocol:
            time.sleep(2)
            while True:
                global message_sended
                while not message_sended:
                    time.sleep(0.1)
                message_to_send = input("type message to send:" + os.linesep)
                if message_to_send == 'exit':
                    return
                message_sended = False
                protocol.write_line('AT+SEND={}'.format(str(len(message_to_send))))
                time.sleep(0.5)
                protocol.write_line(message_to_send)


if __name__ == '__main__':
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=1)

    chat = Chatter(ser)
    chat.start_chatting()
