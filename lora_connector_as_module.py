import logging
import threading
import time
from abc import abstractmethod

import serial

import variables
from LoraConnectorAbstract import LoraConnectorAbstract, bytes_to_str, str_to_bytes

SEND_MESSAGE = False
lock = threading.Lock()

ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=1)
def execute_command(command, verify_response_list=None):
    lock.acquire()
    logging.debug('sending command...')
    ser.write(bytes(command + variables.TERMINATOR, variables.ENCODING))
    global SEND_MESSAGE
    SEND_MESSAGE = False
    return True


def receive_messages():
    global SEND_MESSAGE

    while not SEND_MESSAGE:
        if ser.in_waiting > 0:
            lock.acquire()
            handle_received_line(str(ser.readline(), variables.ENCODING))
            lock.release()
    logging.debug("stopped receiving messages")


@abstractmethod
def handle_received_line(message):
    print(message)
    lock.release()
    execute_command('AT')


# def start_receiving_thread(self):
#     logging.debug('start receiving thread')
#     self.receiving_thread = threading.Thread(target=self.receive_messages)
#     self.receiving_thread.start()
#
#
# def stop_receiving_thread(self):
#     self.SEND_MESSAGE = True
#     logging.debug("stopped receiving thread")
#     if threading.current_thread().ident != self.receiving_thread.ident:
#         self.receiving_thread.join()
#     self.ser.close()


receiving_thread = threading.Thread(target=receive_messages)
receiving_thread.start()



