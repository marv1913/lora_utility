import logging
import signal
import threading
import time
from contextlib import contextmanager

import serial
from serial.threaded import ReaderThread

import variables
import header
from lora_connector_threaded import LoraConnectorThreaded
from routing_table import RoutingTable


class ProtocolLite(LoraConnectorThreaded):

    def __init__(self, ser_conn):
        super().__init__(ser_conn)
        logging.info('created protocol obj: {}'.format(str(self)))
        self.routing_table = RoutingTable()
        # self.start_receiving_thread()
        self.messenger = None
        receiving_thread = threading.Thread(target=self.receive_messages)
        receiving_thread.start()

    def handle_received_line(self, data):
        self.process_incoming_message(data)
        # self.send_message('0139', 'hey')

    def set_messenger(self, messenger):
        self.messenger = messenger

    def send_header(self, header_str):
        if self.execute_command('AT+SEND={}'.format(str(len(header_str))), verify_response_list=['AT,OK']):
            logging.debug('sending {}'.format(header_str))
            time.sleep(1)
            if self.execute_command(header_str, verify_response_list=['AT,SENDING', 'AT,SENDED']):
                logging.debug('sended')

    def process_incoming_message(self, raw_message):
        try:
            header_obj = header.create_header_obj_from_raw_message(raw_message)
            self.routing_table.add_neighbor_to_routing_table(header_obj)
            if header_obj.flag == header.RouteRequestHeader.HEADER_TYPE:
                self.process_route_request(header_obj)
            elif header_obj.flag == header.MessageHeader.HEADER_TYPE:
                self.process_message_header(header_obj)

        except ValueError as e:
            logging.warning(str(e))

    def send_message(self, destination, payload):
        best_route = self.routing_table.get_best_route_for_destination(destination)
        if len(best_route) == 0:
            logging.info(
                'could not find a route to {}. Sending route request...'.format(destination))
            if self.send_route_request_message(destination):
                best_route = self.routing_table.get_best_route_for_destination(destination)
            else:
                logging.info(
                    'Got no answer on route requested.'.format(destination))
                return

        header_obj = header.MessageHeader(None, variables.MY_ADDRESS, destination, 10, best_route['next_node'],
                                          payload)
        self.send_header(header_obj.get_header_str())

    def send_route_request_message(self, requested_node):
        route_request_header_obj = header.RouteRequestHeader(None, variables.MY_ADDRESS, 'FFFF', 10, requested_node, 0)
        self.send_header(route_request_header_obj.get_header_str())
        attempts = 0
        while attempts < 20:
            time.sleep(0.5)
            if len(self.routing_table.get_best_route_for_destination(requested_node)) != 0:
                logging.debug('new route for {} found'.format(requested_node))
                return True
            else:
                attempts = attempts + 1

        logging.debug('got not answer for route request to {}'.format(requested_node))
        return False

    def process_route_request(self, header_obj):
        # first of all look whether requested node is myself
        if header_obj.requested_node == variables.MY_ADDRESS:
            #      send route reply
            # route_reply_header = header.RouteReplyHeader(None, variables.MY_ADDRESS, )
            logging.info('sending route reply message...')
            self.send_route_reply(header_obj.requested_node, header_obj.source)
        else:
            # if header_obj.requested_node not myself look whether there is a route to requested node
            best_route = self.routing_table.get_best_route_for_destination(header_obj.requested_node)
            if len(best_route) == 0:
                logging.info(
                    'could not find a route to {} to forward route request message'.format(header_obj.requested_node))
            else:
                pass

    #         ToDo forward route request message

    def send_route_reply(self, previous_node, end_node):
        route_reply_header_obj = header.RouteReplyHeader(None, variables.MY_ADDRESS, 'FFFF', 10, previous_node,
                                                         end_node, 0)
        self.send_header(route_reply_header_obj.get_header_str())

    def process_message_header(self, header_obj):
        if header_obj.destination == variables.MY_ADDRESS:
            self.messenger.display_received_message(header_obj)
        elif header_obj.next_node == variables.MY_ADDRESS:
            best_route = self.routing_table.get_best_route_for_destination(header_obj.destination)
            if len(best_route) == 0:
                logging.info(
                    'no routing table entry for {} to forward message found'.format(header_obj.next_node))
            else:
                header_obj.next_node = best_route['next_node']
                logging.info('forwarding message from {source} to {destination} over hop {next_node}'.format(
                    source=header_obj.source, destination=header_obj.destination, next_node=header_obj.next_node))
                header_obj.ttl = header_obj.ttl - 1
                self.send_header(header_obj.get_header_str())
        else:
            logging.debug('ignoring message: {}'.format(str(header_obj)))


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError
