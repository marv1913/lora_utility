import logging
from datetime import time

from messenger import Messenger
from protocol_lite import ProtocolLite

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    protocol = ProtocolLite()

    messenger = Messenger(protocol)
    time.sleep(4)

    messenger.start_chatting()

    # TODO implement function to config lora module before launching UI and get own address from module
