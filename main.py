import logging
import time

import consumer_producer
from messenger import Messenger
from protocol_lite import ProtocolLite

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # module_conf = ModuleConfig(consumer_producer.ser)
    # module_conf.config_module()
    consumer_producer.start_send_receive_threads()

    protocol = ProtocolLite()

    messenger = Messenger(protocol)
    time.sleep(2)

    messenger.start_chatting()

    # TODO implement function to config lora module before launching UI and get own address from module
