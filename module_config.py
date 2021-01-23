import logging

import consumer_producer
import header
import variables


class ModuleConfig:

    def __init__(self, ser):
        self.ser = ser

    def config_module(self, configuration=variables.MODULE_CONFIG):
        configuration = configuration + '\r\n'
        configuration = consumer_producer.str_to_bytes(configuration)
        self.ser.write(configuration)
        status = self.ser.readline()
        status = consumer_producer.bytes_to_str(status).strip()
        logging.debug('status after setting config: {}'.format(status))
        if status == variables.STATUS_OK:
            logging.debug('module config successfully set')
            return True
        logging.warning("could not set module config")
        return False

    def get_current_address(self,):
        raise NotImplementedError()