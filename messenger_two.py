import logging
import time

import variables

from prettytable import PrettyTable

from protocol_lite_two import ProtocolLite


class Messenger:
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
        print(variables.WELCOME_TEXT)
        print("type 'help' to see how this program works:\n")
        active = True
        while active:
            text = input('>\n')
            if text == 'exit':
                active = False
                self.protocol.stop()
            elif text == 'help':
                self.print_help_text()
            elif text == ':l':
                self.print_routing_table()
            elif ':' in text:
                self.change_mode(text)
            else:
                if self.MODE == self.CONFIG_MODE:
                    if text == '?':
                        print('current destination address: {}'.format(self.DESTINATION_ADDRESS))
                    elif text == 'all':
                        print(variables.AVAILABLE_NODES)
                    elif text not in variables.AVAILABLE_NODES:
                        print("address '{}' is not available".format(text))
                    else:
                        self.DESTINATION_ADDRESS = text
                        print('destination address set to: {}'.format(text))
                elif self.MODE == self.SEND_MODE:
                    if self.DESTINATION_ADDRESS is None:
                        print('enter config mode and set destination address before sending first message')
                    else:
                        self.protocol.send_message(self.DESTINATION_ADDRESS, text)

    def change_mode(self, text):
        if text == ':c':
            self.MODE = self.CONFIG_MODE
        elif text == ':s':
            self.MODE = self.SEND_MODE
        elif text == ':l':
            self.MODE = self.LIST_MODE
        else:
            print("mode '{}' does not exist".format(text))
            return
        self.__print_mode()

    def __print_mode(self):
        if self.MODE == self.CONFIG_MODE:
            print('config mode entered')
        if self.MODE == self.SEND_MODE:
            print('send mode entered')
        if self.MODE == self.LIST_MODE:
            print('list mode entered')

    def print_routing_table(self):
        routing_table = self.protocol.routing_table.routing_table
        table = PrettyTable()
        table.field_names = ['destination', 'next_node', 'hops']
        for entry in routing_table:
            table.add_row(list(entry.values()))
        for entry in self.protocol.routing_table.unsupported_devices:
            table.add_row([entry, 'n/a', 'n/a'])
        print(table)

    def display_received_message(self, message_header_obj):
        print('received message from {source}: {payload}'.format(source=message_header_obj.source,
                                                                 payload=message_header_obj.payload))

    def print_help_text(self):
        print('\nthere are 2 modes:\n'
              '     send mode   -   :s\n'
              '     config mode -   :c\n\n'
              'e.g. to enter the send mode type in ":s"\n\n'
              'in send mode you can type in a text which is sended to the address which was set by the user\n'
              ''
              'in config mode you have three options:\n'
              '     "all"   to see all available addresses\n'
              '     "?"     to get set address\n'
              '     type in a address to change destination address\n'
              '\n'
              'in each mode you can type ":l" to get the current routing table\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    protocol = ProtocolLite()

    messenger = Messenger(protocol)
    protocol.set_messenger(messenger)
    time.sleep(1)

    messenger.start_chatting()
