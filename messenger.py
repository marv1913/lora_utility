import logging
import time

import serial

import main
from lora_connector_threaded import LoraConnectorThreadedSyncedResponse
from protocol_lite import ProtocolLite


class Messenger(LoraConnectorThreadedSyncedResponse):
    CONFIG_MODE = 0
    SEND_MODE = 1
    MODE = CONFIG_MODE

    def __init__(self, ser_conn):
        super().__init__(ser_conn)
        self.protocol = ProtocolLite()

    def handle_received_line(self, message):
        logging.debug('message: ' + message)
        self.protocol.process_incoming_message(message)

    def send_message(self, message):
        if self.execute_command('AT+SEND={}'.format(str(len(message))), verify_response_list=['AT,OK']):
            print('sending message...')
            if self.execute_command(message, verify_response_list=['AT,SENDING', 'AT,SENDED']):
                print('message sended!')

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


if __name__ == '__main__':
    lora_conn = main.LoraConnector()
    # lora_conn.config_module()

    # response = lora_conn.send_message('ja', wait_for_answer=True)
    #
    # while True:
    #     lora_conn.wait_for_message()
    logging.basicConfig(level=logging.DEBUG)

    ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=30)
    messenger = Messenger(ser)
    messenger.start_receiving_thread()
    # time.sleep(1)
    # messenger.start_chatting()
