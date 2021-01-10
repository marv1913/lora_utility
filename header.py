import logging

import variables

__author__ = "Marvin Rausch"


class Header:
    MIN_LENGTH_RAW_MESSAGE = 16

    def __init__(self, received_from, source, flag, ttl):
        # address of node where the message comes from (LR,{addr},...)
        self.received_from = received_from
        self.source = source
        self.flag = flag
        self.ttl = int(ttl)


def create_header_obj_from_raw_message(raw_message):
    flag = get_flag_from_raw_message(raw_message)

    received_from = get_received_from_value(raw_message)
    check_addr_field(received_from, 'received_from')

    header_str = get_raw_message_as_list(raw_message)[3]
    header_str = header_str.strip()

    source = header_str[0:4]
    check_addr_field(source, 'source')

    ttl = header_str[5:6]
    check_int_field(ttl)

    if flag == MessageHeader.HEADER_TYPE:
        destination = header_str[6:10]
        if destination not in variables.AVAILABLE_NODES:
            raise ValueError(
                "unknown destination: {destination} \n available destinations are {available_destinations}".format(
                    destination=destination, available_destinations=str(variables.AVAILABLE_NODES)))

        next_node = header_str[10:14]
        check_addr_field(next_node, 'next_node')
        payload = header_str[14:]
        if len(payload) == 0:
            raise ValueError('payload is empty!')
        return MessageHeader(received_from, source, ttl, destination, next_node, payload)
    elif flag == RouteRequestHeader.HEADER_TYPE or flag == RouteReplyHeader.HEADER_TYPE:
        # it is a route request or a route reply header
        hops = header_str[6:7]
        check_int_field(hops)

        end_node = header_str[7:11]
        check_addr_field(end_node, 'end_node')

        if flag == RouteRequestHeader.HEADER_TYPE:
            if len(header_str) != RouteRequestHeader.LENGTH:
                raise ValueError('route request header has an unexpected length')
            return RouteRequestHeader(received_from, source, ttl, hops, end_node)

        next_node = header_str[11:15]
        check_addr_field(next_node, 'next_node')

        return RouteReplyHeader(received_from, source, ttl, hops, end_node, next_node)
    raise ValueError("flag '{}' is not a valid flag".format(flag))


def check_int_field(two_digit_value_str, length=1):
    if len(two_digit_value_str) != length:
        int(two_digit_value_str)


def check_addr_field(addr_str, field_name):
    if len(addr_str) != 4:
        raise ValueError(
            "header field '{field_name}' has an unexpected format: {addr_str}".format(field_name=field_name,
                                                                                      addr_str=addr_str))


def get_received_from_value(raw_message):
    """
    get source of message (physical source - value after LR,..)
    :param raw_message: message where to search for 'received_from' value
    :return: source of message as str
    """
    response_as_list = get_raw_message_as_list(raw_message)
    if response_as_list[0] == 'LR':
        return response_as_list[1]
    else:
        raise ValueError('header has a unexpected format: {}'.format(raw_message))


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
        return self.source + str(self.flag) + str(self.ttl) + str(self.hops) + self.end_node


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
        return self.source + str(self.flag) + str(self.ttl) + str(
            self.hops) + self.end_node + self.next_node


class MessageHeader(Header):
    LENGTH = 14
    HEADER_TYPE = 1

    def __init__(self, received_from, source, ttl, destination, next_node, payload):
        super().__init__(received_from, source, self.HEADER_TYPE, ttl)
        self.next_node = next_node
        self.payload = payload
        self.destination = destination

    def get_header_str(self):
        return self.source + str(self.flag) + str(self.ttl) + self.destination + \
               self.next_node + self.payload


class RouteErrorHeader(Header):
    LENGTH = 10
    HEADER_TYPE = 5

    def __init__(self, received_from, source, ttl, broken_node):
        super().__init__(received_from, source, self.HEADER_TYPE, ttl)
        self.broken_node = broken_node

    def get_header_str(self):
        return self.source + str(self.flag) + str(self.ttl) + self.broken_node
