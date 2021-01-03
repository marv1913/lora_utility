import unittest

import header

__author__ = "Marvin Rausch"

class HeaderTest(unittest.TestCase):

    def test_get_received_from_value_good(self):
        self.assertEqual('0137', header.get_received_from_value('LR,0137,10'))

    def test_get_received_from_value_bad_empty_str(self):
        self.assertRaises(ValueError, header.get_received_from_value, '')

    def test_create_route_request_header_obj_good(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,013601370310013801')
        self.assertEqual(header_obj.source, '0136')
        self.assertEqual(header_obj.destination, '0137')
        self.assertEqual(header_obj.flag, 3)
        self.assertEqual(header_obj.ttl, 10)
        self.assertEqual(header_obj.requested_node, '0138')
        self.assertEqual(header_obj.hops, 1)

    def test_create_route_request_header_obj_bad_hops_missing(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,0136013703100138')

    def test_create_route_request_header_bad_to_many_args(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,0131FFFF03100139013100')

    def test_create_route_reply_header_obj_good(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,0136013704100138013302')
        self.assertEqual(header_obj.source, '0136')
        self.assertEqual(header_obj.destination, '0137')
        self.assertEqual(header_obj.flag, 4)
        self.assertEqual(header_obj.ttl, 10)
        self.assertEqual(header_obj.previous_node, '0138')
        self.assertEqual(header_obj.end_node, '0133')
        self.assertEqual(header_obj.hops, 2)

    def test_create_route_reply_header_obj_bad_invalid_flag(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,013601370510013802')

    def test_create_message_header_obj_good(self):
        header_obj = header.create_header_obj_from_raw_message('LR,0136,10,0136013701100138hello')
        self.assertEqual(header_obj.source, '0136')
        self.assertEqual(header_obj.destination, '0137')
        self.assertEqual(header_obj.flag, 1)
        self.assertEqual(header_obj.ttl, 10)
        self.assertEqual(header_obj.next_node, '0138')
        self.assertEqual(header_obj.payload, 'hello')

    def test_create_message_header_obj_bad_payload_missing(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,0136,10,0136013701100138')

    def test_create_header_obj_bad_message_without_header(self):
        self.assertRaises(ValueError, header.create_header_obj_from_raw_message, 'LR,FFFF,0A,hello')




