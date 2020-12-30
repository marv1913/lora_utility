import variables


class Header:
    MIN_LENGTH_RAW_MESSAGE = 16

    def __init__(self, raw_message):
        # address of node where the message comes from (LR,{addr},...)
        self.received_from = get_received_from_value(raw_message)


def create_header_from_raw_message(raw_message):
    if len(raw_message) < Header.MIN_LENGTH_RAW_MESSAGE:
        return None


def check_header(header_obj):
    flag = header_obj.flag
    if len(header_obj.source) != 4:
        raise ValueError("header field 'source' has an unexpected format: {}".format(header_obj.source))
    if header_obj.destination not in variables.AVAILABLE_NODES:
        raise ValueError(
            "unknown destination: {destination}\ available destinations are {available_destinations}".format(
                destination=header_obj.destination, available_destinations=str(variables.AVAILABLE_NODES)))
    check_two_digit_int_field(header_obj.ttl)
    if flag == RouteRequestHeader.HEADER_TYPE or flag == RouteReplyHeader.HEADER_TYPE:
        check_two_digit_int_field(header_obj.hops)
        if flag == RouteRequestHeader.HEADER_TYPE:
            check_addr_field(header_obj.requested_node, 'requested_node')
        else:
            check_addr_field(header_obj.previous_node, 'previous_node')
    elif flag == MessageHeader.HEADER_TYPE:
        if len(header_obj.payload) == 0:
            raise ValueError('payload is empty!')
    else:
        raise ValueError("flag '{}' is not a valid flag".format(flag))
    return flag


def check_two_digit_int_field(two_digit_value_str):
    if len(two_digit_value_str) != 2:
        int(two_digit_value_str)


def check_addr_field(addr_str, field_name):
    if len(addr_str) != 4:
        raise ValueError(
            "header field '{field_name}' has an unexpected format: {addr_str}".format(field_name=field_name,
                                                                                      addr_str=addr_str))


def get_received_from_value(raw_message):
    response_as_list = raw_message.split(',')
    if response_as_list[0] == 'LR':
        return response_as_list[1]
    else:
        raise ValueError('header has a unexpected format: {}'.format(raw_message))


def get_flag_from_raw_message(raw_message):
    flag = raw_message[8:10]
    flag = int(flag)
    return flag


class RouteRequestHeader:
    LENGTH = 18
    HEADER_TYPE = 3

    def __init__(self, source, destination, flag, ttl, requested_node, hops):
        self.source = source
        self.destination = destination
        self.flag = flag
        self.ttl = ttl
        self.requested_node = requested_node
        self.hops = hops

    def __str__(self):
        """
        to string method to make obj human readable for debugging purposes
        :return:
        """
        return self.source + " " + self.destination + " " + self.flag + " " + self.ttl + " " + self.requested_node + \
               " " + self.hops


class RouteReplyHeader:
    LENGTH = 18
    HEADER_TYPE = 4

    def __init__(self, source, destination, flag, ttl, previous_node, hops):
        self.source = source
        self.destination = destination
        self.flag = flag
        self.ttl = ttl
        self.previous_node = previous_node
        self.hops = hops


class MessageHeader:
    LENGTH = 18
    HEADER_TYPE = 1

    def __init__(self, source, destination, flag, ttl, next_node, payload):
        self.source = source
        self.destination = destination
        self.flag = flag
        self.ttl = ttl
        self.next_node = next_node
        self.payload = payload
