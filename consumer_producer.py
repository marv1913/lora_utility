import threading
import queue
import time
import logging

import serial

import variables

__author__ = "Marvin Rausch"

ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=20)

# read_file = 'C:/temp/temp1/simplified.txt'
# log1 = open('C:/temp/temp1/simplified_log1.txt', "a+")

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )

BUF_SIZE = 100
q = queue.Queue(BUF_SIZE)
BUF_SIZE = 1000
response_q = queue.Queue(BUF_SIZE)
BUF_SIZE = 1000
status_q = queue.Queue(BUF_SIZE)
WRITE_DATA = False
PRODUCER_THREAD_ACTIVE = True
CONSUMER_THREAD_ACTIVE = True


def bytes_to_str(message_in_bytes):
    return message_in_bytes.decode(variables.ENCODING)


def str_to_bytes(string_to_convert):
    return bytes(string_to_convert, variables.ENCODING)


class ProducerThread(threading.Thread):
    def __init__(self, name):
        super(ProducerThread, self).__init__()
        self.name = name

    def run(self):
        global PRODUCER_THREAD_ACTIVE
        while PRODUCER_THREAD_ACTIVE:
            global WRITE_DATA
            if q.empty() and not WRITE_DATA:
                # print('reading')

                if ser.in_waiting:
                    print('read')
                    response_q.put(bytes_to_str(ser.readline()))

            # else:
            #     print('locked')
            #     time.sleep(1)


class ConsumerThread(threading.Thread):
    def __init__(self, name):
        super(ConsumerThread, self).__init__()
        self.name = name
        return

    def run(self):
        global CONSUMER_THREAD_ACTIVE
        while CONSUMER_THREAD_ACTIVE:
            if not q.empty():
                global WRITE_DATA
                WRITE_DATA = True
                command_tuple = q.get()
                command = command_tuple[0]
                command = command + '\r\n'
                command = str_to_bytes(command)
                verify_list = command_tuple[1]
                logging.debug("sending command '{}'".format(command))
                ser.write(command)
                successful = True
                if len(verify_list) > 0:
                    for entry in verify_list:
                        status = bytes_to_str(ser.readline())
                        status = status.strip()
                        if entry != status:
                            logging.warning(
                                'could not verify {expected} != {status}'.format(expected=entry, status=status))
                            status = False
                        else:
                            logging.debug('verified {status}'.format(status=status))
                    status_q.put(successful)

                time.sleep(0.2)
                WRITE_DATA = False


if __name__ == '__main__':
    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    time.sleep(0.5)
    c.start()
    time.sleep(0.5)
    q.put(('AT', ['AT,OK']))
    q.put(('AT', []))

    time.sleep(2)
    print(response_q.get())
