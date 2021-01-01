from abc import abstractmethod

import variables


def bytes_to_str(message_in_bytes):
    return message_in_bytes.decode(variables.ENCODING)


def str_to_bytes(string_to_convert):
    return bytes(string_to_convert, variables.ENCODING)


class LoraConnectorAbstract:

    @abstractmethod
    def execute_command(self, command):
        ...

    # @abstractmethod
    # def receive_messages(self):
    #     ...
    #
    # @abstractmethod
    # def handle_line(self, message):
    #     ...

    def config_module(self, save_config=True):
        for command in variables.CONFIG_COMMAND_LIST:
            self.execute_command(command)
        if save_config:
            self.execute_command(variables.SAVE_COMMAND)
