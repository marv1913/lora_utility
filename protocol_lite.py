import logging

import variables
import header
from routing_table import RoutingTable


class ProtocolLite:

    def __init__(self):
        logging.info('created protocol obj: {}'.format(str(self)))
        self.routing_table = RoutingTable()

    def process_incoming_message(self, raw_message):
        try:
            header_obj = header.Header(raw_message)
            self.routing_table.add_neighbor_to_routing_table(header_obj)
        except ValueError as e:
            logging.warning(str(e))




def get_protocol_obj_from_raw_message(raw_message):
    """
    get a ProtocolLite obj from raw message
    :param raw_message: raw message from received from another peer
    :return: ProtocolLite obj with parameters from raw_message
    """
    response_as_list = raw_message.split(',')
    if len(response_as_list) != 4:
        logging.warning('raw message has bad format: {}'.format(raw_message))
        return None
    header_as_str = response_as_list[3]
    if len(header_as_str) < 14:
        logging.warning('header has bad format: {}'.format(header_as_str))
        return None

    source_address = header_as_str[0:4]
    destination_address = header_as_str[4:8]
    flags = header_as_str[8:10]
    ttl = header_as_str[10:12]
    sequence_number = header_as_str[12:14]
    payload = header_as_str[14:len(header_as_str)]
    return ProtocolLite(source_address, destination_address, flags, ttl, payload)
