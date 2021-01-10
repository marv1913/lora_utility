import logging
import signal
import threading
import time
from contextlib import contextmanager

import consumer_producer
import variables
import header
import view
from routing_table import RoutingTable

__author__ = "Marvin Rausch"


class ProtocolLite:
    PROCESS_INCOMING_MESSAGES = True
    VERIFICATION_TIMEOUT = 25

    def __init__(self):
        logging.info('created protocol obj: {}'.format(str(self)))
        self.routing_table = RoutingTable()
        receiving_thread = threading.Thread(target=self.process_incoming_message)
        receiving_thread.start()
        p = consumer_producer.ProducerThread(name='producer')
        c = consumer_producer.ConsumerThread(name='consumer')

        p.start()
        time.sleep(0.5)
        c.start()
        time.sleep(0.5)

    def send_header(self, header_str):
        consumer_producer.q.put(('AT+SEND={}'.format(str(len(header_str))), ['AT,OK']))
        if consumer_producer.status_q.get(timeout=self.VERIFICATION_TIMEOUT):
            consumer_producer.q.put((header_str, ['AT,SENDING', 'AT,SENDED']))
            if consumer_producer.status_q.get(timeout=self.VERIFICATION_TIMEOUT):
                logging.debug("header '{}' sended.".format(header_str))
                return
        logging.debug("could not send header '{}', because got invalid status from lora module".format(header_str))

    def process_incoming_message(self):
        while self.PROCESS_INCOMING_MESSAGES:
            if not consumer_producer.response_q.empty():
                raw_message = consumer_producer.response_q.get()

                try:
                    header_obj = header.create_header_obj_from_raw_message(raw_message)
                    self.routing_table.add_neighbor_to_routing_table(header_obj)
                    if header_obj.flag == header.RouteRequestHeader.HEADER_TYPE:
                        self.process_route_request(header_obj)
                    elif header_obj.flag == header.MessageHeader.HEADER_TYPE:
                        self.process_message_header(header_obj)

                except ValueError as e:
                    logging.warning(str(e))
                    try:
                        logging.debug('try to add received signal to unsupported devices list...')
                        addr = header.get_received_from_value(raw_message)
                        self.routing_table.add_neighbor_with_unsupported_protocol(addr)
                    except ValueError:
                        pass

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

        header_obj = header.MessageHeader(None, variables.MY_ADDRESS, 9, destination, best_route['next_node'],
                                          payload)
        self.send_header(header_obj.get_header_str())

    def send_route_request_message(self, end_node):
        route_request_header_obj = header.RouteRequestHeader(None, variables.MY_ADDRESS, variables.DEFAULT_TTL, 1,
                                                             end_node)
        self.send_header(route_request_header_obj.get_header_str())
        with timeout(variables.ROUTE_REQUEST_TIMEOUT):
            while True:
                try:
                    if len(self.routing_table.get_best_route_for_destination(end_node)) != 0:
                        logging.debug('new route for {} found'.format(end_node))
                        return True
                    time.sleep(0.5)
                except ValueError:
                    logging.debug('got not answer for route request to {}'.format(end_node))
                    return False

    def process_route_request(self, header_obj):
        # first of all check whether source of route request is myself (to prevent cycle)
        if header_obj.source != variables.MY_ADDRESS:
            # look whether requested node is myself
            if header_obj.end_node == variables.MY_ADDRESS:
                #      send route reply
                # route_reply_header = header.RouteReplyHeader(None, variables.MY_ADDRESS, )
                logging.info('sending route reply message...')
                self.send_route_reply(next_node=header_obj.received_from, end_node=header_obj.source)
            else:
                if len(self.routing_table.get_best_route_for_destination(header_obj.source)) == 0:
                    # if there is no entry for source of route request, you can add routing table entry
                    self.routing_table.add_routing_table_entry(header_obj.source, header_obj.received_from,
                                                               header_obj.hops)
                header_obj.ttl = header_obj.ttl - 1
                header_obj.hops = header_obj.hops + 1
                if not self.routing_table.check_route_request_already_processed(header_obj.end_node):
                    logging.debug('forward route request message')
                    self.routing_table.add_address_to_processed_requests_list(header_obj.end_node)
                    self.send_header(header_obj.get_header_str())
                else:
                    logging.debug('route request was already processed')

                # end_node = header_obj.end_node
                # # wait for route reply
                #
                #
                # with timeout(variables.ROUTE_REQUEST_TIMEOUT):
                #     while True:
                #         try:
                #             if len(self.routing_table.get_best_route_for_destination(end_node)) != 0:
                #                 logging.debug('new route for {} found'.format(end_node))
                #                 break
                #             time.sleep(0.5)
                #         except ValueError:
                #             # send route error
                #             logging.debug('got not answer for route request to {}'.format(end_node))
                #             # self.send_route_error(header_obj.end_node)

    def send_route_reply(self, next_node, end_node):
        route_reply_header_obj = header.RouteReplyHeader(None, variables.MY_ADDRESS, variables.DEFAULT_TTL, 1,
                                                         end_node, next_node)
        self.send_header(route_reply_header_obj.get_header_str())

    def process_message_header(self, header_obj):
        if header_obj.destination == variables.MY_ADDRESS:
            view.display_received_message(header_obj)
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

    def process_route_reply_header(self, header_obj):
        if header_obj.source == variables.MY_ADDRESS:
            # add entry to routing table
            self.routing_table.add_routing_table_entry(header_obj.end_node, header_obj.received_from, header_obj.hops)
        elif header_obj.next_node == variables.MY_ADDRESS:
            if len(self.routing_table.get_best_route_for_destination(header_obj.source)) != 0:
                # forward route reply message
                # add routing table entry
                self.routing_table.add_routing_table_entry(header_obj.end_node, header_obj.received_from,
                                                           header_obj.hops)
                # forward message
                header_obj.next_node = self.routing_table.get_best_route_for_destination(header_obj.source)['next_node']
                header_obj.hops = header_obj.hops + 1
                header_obj.ttl = header_obj.ttl - 1
                self.send_header(header_obj.get_header_str())
            else:
                # send route error, because there is no route to forward route reply message to
                # source node of route request
                logging.info(
                    'can not forward route reply message, ,because there is no route to forward route reply message to')
                # source node of route request')
                # self.send_route_error(header_obj.source)

    def send_route_error(self, end_node):
        route_error_header_obj = header.RouteErrorHeader(None, variables.MY_ADDRESS, 9,
                                                         end_node)
        self.send_header(route_error_header_obj.get_header_str())

    def stop(self):
        self.PROCESS_INCOMING_MESSAGES = False
        consumer_producer.CONSUMER_THREAD_ACTIVE = False
        consumer_producer.PRODUCER_THREAD_ACTIVE = False


@contextmanager
def timeout(time_in_sec):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time_in_sec)
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
