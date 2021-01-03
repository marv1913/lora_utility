import logging

import variables


class Header:
    MIN_LENGTH_RAW_MESSAGE = 16

    def __init__(self, received_from, source, destination, flag, ttl):
        # address of node where the message comes from (LR,{addr},...)
        self.received_from = received_from
        self.source = source
        self.destination = destination
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

    destination = header_str[4:8]
    if destination not in variables.AVAILABLE_NODES:
        raise ValueError(
            "unknown destination: {destination} \n available destinations are {available_destinations}".format(
                destination=destination, available_destinations=str(variables.AVAILABLE_NODES)))

    ttl = header_str[10:12]
    check_two_digit_int_field(ttl)

    if flag == RouteRequestHeader.HEADER_TYPE:
        if len(header_str) != RouteRequestHeader.LENGTH:
            raise ValueError('header too long')
        hops = header_str[16:18]
        check_two_digit_int_field(hops)
        requested_node = header_str[12:16]
        check_addr_field(requested_node, 'requested_node')
        return RouteRequestHeader(received_from, source, destination, ttl, requested_node, hops)
    elif flag == RouteReplyHeader.HEADER_TYPE:
            hops = header_str[20:22]
            check_two_digit_int_field(hops)
            previous_node = header_str[12:16]
            end_node = header_str[16:20]
            check_addr_field(previous_node, 'previous_node')
            return RouteReplyHeader(received_from, source, destination, ttl, previous_node, end_node, hops)
    elif flag == MessageHeader.HEADER_TYPE:
        next_node = header_str[12:16]
        check_addr_field(next_node, 'next_node')
        payload = header_str[16:]
        if len(payload) == 0:
            raise ValueError('payload is empty!')
        return MessageHeader(received_from, source, destination, ttl, next_node, payload)
    else:
        raise ValueError("flag '{}' is not a valid flag".format(flag))


def check_two_digit_int_field(two_digit_value_str):
    if len(two_digit_value_str) != 2:
        int(two_digit_value_str)


def check_addr_field(addr_str, field_name):
    if len(addr_str) != 4:
        raise ValueError(
            "header field '{field_name}' has an unexpected format: {addr_str}".format(field_name=field_name,
                                                                                      addr_str=addr_str))


def get_received_from_value(raw_message):
    response_as_list = get_raw_message_as_list(raw_message)
    if response_as_list[0] == 'LR':
        return response_as_list[1]
    else:
        raise ValueError('header has a unexpected format: {}'.format(raw_message))


def get_flag_from_raw_message(raw_message):
    try:
        header_str = get_raw_message_as_list(raw_message)[3]
        flag = header_str[8:10]
        flag = int(flag)
    except IndexError:
        raise ValueError('flag was not set')
    return flag


def get_raw_message_as_list(raw_message):
    return raw_message.split(',')


def get_two_digit_str(int_value):
    if len(str(int_value)) == 1:
        return '0' + str(int_value)
    else:
        return str(int_value)


class RouteRequestHeader(Header):
    LENGTH = 18
    HEADER_TYPE = 3

    def __init__(self, received_from, source, destination, ttl, requested_node, hops):
        super().__init__(received_from, source, destination, self.HEADER_TYPE, ttl)
        self.requested_node = requested_node
        self.hops = int(hops)

    def __str__(self):
        """
        to string method to make obj human readable for debugging purposes
        :return:
        """
        return self.source + " " + self.destination + " " + self.flag + " " + self.ttl + " " + self.requested_node + \
               " " + self.hops

    def get_header_str(self):
        return self.source + self.destination + get_two_digit_str(self.flag) + get_two_digit_str(self.ttl) + \
               self.requested_node + get_two_digit_str(self.hops)


class RouteReplyHeader(Header):
    LENGTH = 18
    HEADER_TYPE = 4

    def __init__(self, received_from, source, destination, ttl, previous_node, end_node, hops):
        super().__init__(received_from, source, destination, self.HEADER_TYPE, ttl)
        self.previous_node = previous_node
        self.end_node = end_node
        self.hops = int(hops)

    def get_header_str(self):
        return self.source + self.destination + get_two_digit_str(self.flag) + get_two_digit_str(self.ttl) + \
               self.previous_node + self.end_node + get_two_digit_str(self.hops)

class MessageHeader(Header):
    LENGTH = 18
    HEADER_TYPE = 1

    def __init__(self, received_from, source, destination, ttl, next_node, payload):
        super().__init__(received_from, source, destination, self.HEADER_TYPE, ttl)
        self.next_node = next_node
        self.payload = payload

    def get_header_str(self):
        return self.source + self.destination + get_two_digit_str(self.flag) + get_two_digit_str(self.ttl) + \
               self.next_node + self.payload
