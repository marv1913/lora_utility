import logging

import variables


class RoutingTable:

    def __init__(self):
        self.routing_table = []

    def add_routing_table_entry(self, destination, next_node, hops):
        new_routing_table_entry = {'destination': destination, 'next_node': next_node, 'hops': hops}
        if not self.check_routing_table_entry_exists(destination, next_node, hops):
            logging.debug('new entry in routing table: {}'. format(str(new_routing_table_entry)))
            self.routing_table.append(new_routing_table_entry)
        else:
            logging.debug('entry already exists: {}'.format(str(new_routing_table_entry)))

    def check_routing_table_entry_exists(self, destination, next_node, hops):
        for entry in self.routing_table:
            if entry['destination'] == destination and entry['next_node'] == next_node and entry['hops'] == hops:
                return True
        return False

    def add_neighbor_to_routing_table(self, header_obj):
        logging.debug('call add neighbor function')
        received_from = header_obj.received_from
        self.add_routing_table_entry(received_from, received_from, 0)
