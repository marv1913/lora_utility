import time

import serial

from lora_connector_threaded import LoraConnectorThreadedSyncedResponse


class EchoTester(LoraConnectorThreadedSyncedResponse):

    def __init__(self, ser_conn):
        super().__init__(ser_conn)
        self.other_peers = []

    def handle_received_line(self, message):
        response_as_list = message.split(',')
        if response_as_list[0] == 'LR':
            print('got message from {sender} with length {length}: {message}'.format(sender=response_as_list[1],
                                                                                     length=response_as_list[2],
                                                                                     message=response_as_list[3]))
            if response_as_list[1] not in self.other_peers:
                self.other_peers.append(response_as_list[1])
                print(self.other_peers)

        else:
            print(message)

    def send_message(self, message):
        if self.execute_command('AT+SEND={}'.format(str(len(message))), verify_response_list=['AT,OK']):
            print('sending message...')
            if self.execute_command(message):
                print('message sended!')
        else:
            print('error')

    def start_sending_messages(self):
        while True:
            self.send_message('hello')
            time.sleep(15)

if __name__ == '__main__':
    ser = serial.serial_for_url('/dev/ttyS0', baudrate=115200, timeout=5)
    echo_utility = EchoTester(ser)
    echo_utility.start_receiving_thread()
    echo_utility.start_sending_messages()