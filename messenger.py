import logging
import time

import serial

import main
from protocol_lite import ProtocolLite


class Messenger():
    CONFIG_MODE = 0
    SEND_MODE = 1
    MODE = CONFIG_MODE

    def __init__(self, protocol):
        self.protocol = protocol
        self.protocol.set_messenger(self)

    def chat_beta(self):
        while True:
            text = input("type 'help' to see how this program works:\n")
            self.protocol.send_message('0131', text)

    def start_chatting(self):
        text = input("type 'help' to see how this program works:\n")
        if ':' in text:
            # in config mode
            if text == ':config':
                self.MODE = self.CONFIG_MODE
                self.print_mode()
            if text == ':send':
                self.MODE = self.SEND_MODE
                self.print_mode()
        if text == 'help':
            print('here you could get some support')

        self.send_message(text)

    def print_mode(self):
        if self.MODE == self.CONFIG_MODE:
            print('config mode entered')
        if self.MODE == self.SEND_MODE:
            print('send mode entered')

    def display_received_message(self, message_header_obj):
        print('received message from {source}: {payload}'.format(source=message_header_obj.source,
                                                                 payload=message_header_obj.payload))


if __name__ == '__main__':
    # lora_conn.config_module()

    # response = lora_conn.send_message('ja', wait_for_answer=True)
    #
    # while True:
    #     lora_conn.wait_for_message()
    logging.basicConfig(level=logging.DEBUG)
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=5)
    protocol = ProtocolLite(ser)
    # protocol.send_message('0137', 'hey')

    messenger = Messenger(protocol)
    protocol.set_messenger(messenger)


    messenger.chat_beta()
