class Header:
    MIN_LENGTH_RAW_MESSAGE = 16

    def __init__(self, raw_message):
        # address of node where the message comes from (LR,{addr},...)
        self.received_from = get_received_from_value(raw_message)


def create_header_from_raw_message(raw_message):
    if len(raw_message) < Header.MIN_LENGTH_RAW_MESSAGE:
        return None
    flag = get_flag_from_raw_message(raw_message)
    if flag == RouteRequestHeader.HEADER_TYPE:
        # it is a route request header
        pass
    elif flag == RouteReplyHeader.HEADER_TYPE:
        # it is a route reply header
        pass
    elif flag == MessageHeader.HEADER_TYPE:
        # it is a header of a chat message
        pass
    else:
        # invalid flag
        pass


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
