import logging
import threading
import time
from abc import abstractmethod

import serial

import variables
from LoraConnectorAbstract import LoraConnectorAbstract, bytes_to_str, str_to_bytes

lock = threading.Lock()


class LoraConnectorThreaded:
    SEND_MESSAGE = False

    def __init__(self, ser_conn):
        logging.debug('instantiated LoraConnector')

        self.ser = ser_conn

    def execute_command(self, command, verify_response_list=None):
        successful = True
        self.SEND_MESSAGE = True
        self.ser.write(bytes(command + variables.TERMINATOR, variables.ENCODING))
        if verify_response_list is not None:
            for entry in verify_response_list:
                status = str(self.ser.readline(), variables.ENCODING).strip()
                if entry != status:
                    print(entry)
                    print(status)
                    print('could not verify response')
                    successful = False
        time.sleep(0.2)
        self.SEND_MESSAGE = False

        return successful

    def receive_messages(self):
        while True:
            if not self.SEND_MESSAGE and self.ser.in_waiting > 0:
                logging.debug('receiving')
                self.handle_received_line(str(self.ser.readline(), variables.ENCODING))

    @abstractmethod
    def handle_received_line(self, message):
        print(message)
        if 'hey' in message:
            self.execute_command('AT')

        # self.execute_command('AT')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=5)
    lora_threaded = LoraConnectorThreaded(ser)
    t = threading.Thread(target=lora_threaded.receive_messages)
    t.start()
    time.sleep(1)
    lora_threaded.execute_command('AT+SEND=2')
    lora_threaded.execute_command("hey")
    lora_threaded.execute_command('AT+SEND=2')
    lora_threaded.execute_command("hey")
    lora_threaded.execute_command('AT+SEND=2')
    lora_threaded.execute_command("hey")
    lora_threaded.execute_command('AT+SEND=2')
    lora_threaded.execute_command("hey")
