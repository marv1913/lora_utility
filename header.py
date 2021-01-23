import logging

import variables

__author__ = "Marvin Rausch"

EXPECTED_VALUE_COUNT_ROUTE_REQUEST_HEADER = 5
EXPECTED_VALUE_COUNT_ROUTE_REPLY_HEADER = 6
EXPECTED_VALUE_COUNT_MESSAGE_HEADER = 6


class Header:

    def __init__(self, received_from, source, flag, ttl):
        # address of node where the message comes from (LR,{addr},...)
        self.received_from = received_from
        self.source = source
        self.flag = flag
        self.ttl = int(ttl)


def create_header_obj_from_raw_message(raw_message):
    try:
        raw_message_as_list = raw_message.split(variables.LORA_MODULE_DELIMITER)

        received_from = raw_message_as_list[1]
        check_addr_field(received_from, 'received_from')

        header_str = raw_message_as_list[3]
        # header_str = header_str.strip()

        header_as_list = header_str.split(variables.HEADER_DELIMITER)
        del header_as_list[0]  # remove first and last element, because they are empty strings (delimiter without values)
        del header_as_list[len(header_as_list)-1]  # remove first and last element, because they are empty strings (delimiter without values)


        source = header_as_list[0]
        check_addr_field(source, 'source')

        flag = header_as_list[1]
        check_int_field(flag)
        flag = int(flag)

        ttl = header_as_list[2]
        check_int_field(ttl)

        if flag == MessageHeader.HEADER_TYPE:
            destination = header_as_list[3]
            if destination not in variables.AVAILABLE_NODES:
                raise ValueError(
                    "unknown destination: {destination} \n available destinations are {available_destinations}".format(
                        destination=destination, available_destinations=str(variables.AVAILABLE_NODES)))

            next_node = header_as_list[4]
            check_addr_field(next_node, 'next_node')
            payload = header_as_list[5]
            if len(payload) == 0:
                raise ValueError('payload is empty!')
            return MessageHeader(received_from, source, ttl, destination, next_node, payload)
        elif flag == RouteRequestHeader.HEADER_TYPE or flag == RouteReplyHeader.HEADER_TYPE:
            # it is a route request or a route reply header
            hops = header_as_list[3]
            check_int_field(hops)

            end_node = header_as_list[4]
            check_addr_field(end_node, 'end_node')

            if flag == RouteRequestHeader.HEADER_TYPE:
                if len(header_as_list) != EXPECTED_VALUE_COUNT_ROUTE_REQUEST_HEADER:
                    raise ValueError('route request header has an unexpected length')
                return RouteRequestHeader(received_from, source, ttl, hops, end_node)

            next_node = header_as_list[5]
            check_addr_field(next_node, 'next_node')

            return RouteReplyHeader(received_from, source, ttl, hops, end_node, next_node)
        raise ValueError("flag '{}' is not a valid flag".format(flag))
    except IndexError:
        raise ValueError("header has an unexpected length")


def check_int_field(two_digit_value_str, length=1):
    if len(two_digit_value_str) != length:
        int(two_digit_value_str)


def check_addr_field(addr_str, field_name):
    if len(addr_str) != 4:
        raise ValueError(
            "header field '{field_name}' has an unexpected format: {addr_str}".format(field_name=field_name,
                                                                                      addr_str=addr_str))


def get_flag_from_raw_message(raw_message):
    """
    get flag of raw message
    :param raw_message: message as str where to search for flag
    :return: flag as int
    """
    try:
        header_str = get_raw_message_as_list(raw_message)[3]
        flag = header_str[4:5]
        flag = int(flag)
    except IndexError:
        raise ValueError('flag was not set')
    return flag


def get_raw_message_as_list(raw_message):
    return raw_message.split(',')


# def get_two_digit_str(int_value):
#     if len(str(int_value)) == 1:
#         return '0' + str(int_value)
#     else:
#         return str(int_value)


class RouteRequestHeader(Header):
    LENGTH = 11
    HEADER_TYPE = 3

    def __init__(self, received_from, source, ttl, hops, end_node):
        super().__init__(received_from, source, self.HEADER_TYPE, ttl)
        self.end_node = end_node
        self.hops = int(hops)

    def __str__(self):
        """
        to string method to make obj human readable for debugging purposes
        :return:
        """
        return self.source + " " + self.flag + " " + str(self.ttl) + " " + str(self.hops) + " " + self.end_node

    def get_header_str(self):
        return create_header_str(self.source, str(self.flag), str(self.ttl), str(self.hops), self.end_node)


class RouteReplyHeader(Header):
    LENGTH = 15
    HEADER_TYPE = 4

    def __init__(self, received_from, source, ttl, hops, end_node, next_node):
        super().__init__(received_from, source, self.HEADER_TYPE, ttl)
        self.end_node = end_node
        self.hops = int(hops)
        self.next_node = next_node

    def __str__(self):
        """
        to string method to make obj human readable for debugging purposes
        :return:
        """
        return self.source + " " + self.flag + " " + str(self.ttl) + " " + str(self.hops) + " " + self.end_node + \
               " " + self.next_node

    def get_header_str(self):
        return create_header_str(self.source, str(self.flag), str(self.ttl), str(self.hops), self.end_node,
                                 self.next_node)


class MessageHeader(Header):
    LENGTH = 14
    HEADER_TYPE = 1

    def __init__(self, received_from, source, ttl, destination, next_node, payload):
        super().__init__(received_from, source, self.HEADER_TYPE, ttl)
        self.next_node = next_node
        self.payload = payload
        self.destination = destination

    def get_header_str(self):
        return create_header_str(self.source, str(self.flag), str(self.ttl), self.destination, self.next_node,
                                 self.payload)


class RouteErrorHeader(Header):
    LENGTH = 10
    HEADER_TYPE = 5

    def __init__(self, received_from, source, ttl, broken_node):
        super().__init__(received_from, source, self.HEADER_TYPE, ttl)
        self.broken_node = broken_node

    def get_header_str(self):
        return self.source + str(self.flag) + str(self.ttl) + self.broken_node


def create_header_str(*args):
    """
    create header str with delimiters
    :param args: values which should be in header
    :return: values concatenated as str with '|' as delimiter
    """
    header_str = '|'
    for arg in args:
        header_str = header_str + str(arg) + '|'
    return header_str
