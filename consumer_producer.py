import threading
import queue
import time
import logging

import serial

import variables

__author__ = "Marvin Rausch"

ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=20)


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
                if ser.in_waiting:
                    logging.debug('read')
                    received_raw_message = ser.readline()
                    logging.debug('received: {}'.format(received_raw_message))

                    received_raw_message = bytes_to_str(received_raw_message)
                    response_q.put(received_raw_message)

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
                        if 'LR' in status:
                            logging.warning('got message while verifying command: {}. Message dumped.'.format(status))
                            #  dump message, if receiving message while verifying status of command
                            status = bytes_to_str(ser.readline())
                            status = status.strip()
                        if entry != status:
                            logging.warning(
                                'could not verify {expected} != {status}'.format(expected=entry, status=status))
                            successful = False
                        else:
                            logging.debug('verified {status}'.format(status=status))
                    status_q.put(successful)

                time.sleep(0.2)
                WRITE_DATA = False


def start_send_receive_threads():
    t1 = ProducerThread(name='producer')
    t2 = ConsumerThread(name='consumer')

    t1.start()
    time.sleep(0.5)
    t2.start()
    time.sleep(0.5)


def execute_command(command_as_str, verification_list=None):
    if verification_list is None:
        verification_list = []
    q.put((command_as_str, verification_list))
    if len(verification_list) != 0:
        return status_q.get(timeout=variables.COMMAND_VERIFICATION_TIMEOUT)


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
