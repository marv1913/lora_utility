import itertools
import time
import unittest
from unittest.mock import patch, MagicMock

import serial

__author__ = "Marvin Rausch"


class ConsumerProducerTest(unittest.TestCase):

    def setUp(self) -> None:
        self.ser = MagicMock()

    def test_verify_command_good(self):
        with patch.object(serial, 'serial_for_url', return_value=self.ser), patch.object(time, 'sleep',
                                                                                         side_effect=InterruptedError):
            import consumer_producer
            consumer_producer.q.put(('AT', ['OK']))
            self.ser.readline.return_value = consumer_producer.str_to_bytes('OK')
            try:
                consumer_producer.ConsumerThread('test_receiving').run()
            except InterruptedError:
                self.assertFalse(consumer_producer.status_q.empty())
                self.assertTrue(consumer_producer.status_q.get())

    def test_verify_command_bad(self):
        with patch.object(serial, 'serial_for_url', return_value=self.ser), patch.object(time, 'sleep',
                                                                                         side_effect=InterruptedError):
            import consumer_producer
            consumer_producer.q.put(('AT', ['OK']))
            self.ser.readline.side_effect = itertools.chain([consumer_producer.str_to_bytes('LR')],
                                                            itertools.repeat(consumer_producer.str_to_bytes('OK')))
            try:
                consumer_producer.ConsumerThread('test_receiving').run()
            except InterruptedError:
                self.assertFalse(consumer_producer.status_q.empty())
                self.assertTrue(consumer_producer.status_q.get())
