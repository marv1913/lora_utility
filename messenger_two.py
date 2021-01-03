import logging
import time

import variables
from consumer_producer import ProducerThread, ConsumerThread

from prettytable import PrettyTable

from protocol_lite_two import ProtocolLite


class Messenger():
    CONFIG_MODE = 0
    SEND_MODE = 1
    LIST_MODE = 2
    MODE = SEND_MODE
    # DESTINATION_ADDRESS = None
    DESTINATION_ADDRESS = '0131'


    def __init__(self, protocol):
        self.protocol = protocol
        self.protocol.set_messenger(self)

    def chat_beta(self):
        while True:
            text = input("type 'help' to see how this program works:\n")
            self.protocol.send_message('0131', text)

    def start_chatting(self):
        print("type 'help' to see how this program works:\n")
        active = True
        while active:
            text = input('>\n')
            if text == 'exit':
                active = False
                self.protocol.stop()
            elif text == 'help':
                print('here you could get some support')
            elif ':' in text:
                # in config mode
                if text == ':c':
                    self.MODE = self.CONFIG_MODE
                    self.print_mode()
                elif text == ':s':
                    self.MODE = self.SEND_MODE
                    self.print_mode()
                elif text == ':l':
                    self.MODE = self.LIST_MODE
                    self.print_mode()
                else:
                    print("mode '{}' does not exist".format(text))
            else:
                if self.MODE == self.CONFIG_MODE:
                    if text not in variables.AVAILABLE_NODES:
                        print("address '{}' is not available".format(text))
                    else:
                        self.DESTINATION_ADDRESS = text
                        print('destination address set to: {}'.format(text))
                elif self.MODE == self.SEND_MODE:
                    if self.DESTINATION_ADDRESS is None:
                        print('enter config mode and set destination address before sending first message')
                    else:
                        self.protocol.send_message(self.DESTINATION_ADDRESS, text)
                elif self.MODE == self.LIST_MODE:
                    if text == 'show':
                        self.print_routing_table()

    def print_mode(self):
        if self.MODE == self.CONFIG_MODE:
            print('config mode entered')
        if self.MODE == self.SEND_MODE:
            print('send mode entered')

    def print_routing_table(self):
        routing_table = self.protocol.routing_table.routing_table
        table = PrettyTable()
        table.field_names = ['destination', 'next_node', 'hops']
        for entry in routing_table:
            table.add_row(list(entry.values()))
        print(table)

    def display_received_message(self, message_header_obj):
        print('received message from {source}: {payload}'.format(source=message_header_obj.source,
                                                                 payload=message_header_obj.payload))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    protocol = ProtocolLite()

    messenger = Messenger(protocol)
    protocol.set_messenger(messenger)
    time.sleep(3)

    messenger.start_chatting()

