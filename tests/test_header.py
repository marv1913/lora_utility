import unittest

import header

__author__ = "Marvin Rausch"


class HeaderTest(unittest.TestCase):

    def test_get_received_from_value_good(self):
        self.assertEqual('0137', header.get_received_from_value('LR,0137,10'))

    def test_get_received_from_value_bad_empty_str(self):
        self.assertRaises(ValueError, header.get_received_from_value, '')

    def test_create_route_request_header_obj_good(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,013730840138')
        self.assertEqual(header_obj.source, '0137')
        self.assertEqual(header_obj.flag, 3)
        self.assertEqual(header_obj.ttl, 8)
        self.assertEqual(header_obj.end_node, '0138')
        self.assertEqual(header_obj.hops, 4)

    def test_create_route_request_header_obj_bad_hops_missing(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,01373080138')

    def test_create_route_request_header_bad_to_many_args(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,0137308401380')

    def test_create_route_reply_header_obj_good(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,0137408301390140')
        self.assertEqual(header_obj.source, '0137')
        self.assertEqual(header_obj.received_from, '0136')
        self.assertEqual(header_obj.end_node, '0139')
        self.assertEqual(header_obj.next_node, '0140')
        self.assertEqual(header_obj.flag, 4)
        self.assertEqual(header_obj.ttl, 8)
        self.assertEqual(header_obj.hops, 3)

    def test_create_route_reply_header_obj_bad_invalid_flag(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, '0137808301390140')

    def test_create_message_header_obj_good(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,013510301380137hello')
        self.assertEqual(header_obj.source, '0135')
        self.assertEqual(header_obj.destination, '0138')
        self.assertEqual(header_obj.flag, 1)
        self.assertEqual(header_obj.ttl, 3)
        self.assertEqual(header_obj.next_node, '0137')
        self.assertEqual(header_obj.payload, 'hello')
        self.assertEqual(header_obj.received_from, '0136')

    def test_create_message_header_obj_good2(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,013511001380137hello')
        self.assertEqual(header_obj.source, '0135')
        self.assertEqual(header_obj.destination, '0138')
        self.assertEqual(header_obj.flag, 1)
        self.assertEqual(header_obj.ttl, 10)
        self.assertEqual(header_obj.next_node, '0137')
        self.assertEqual(header_obj.payload, 'hello')
        self.assertEqual(header_obj.received_from, '0136')

    def test_create_message_header_obj_bad_payload_missing(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,013511001380137')

    def test_create_header_obj_bad_message_without_header(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,FFFF,0A,hello')
