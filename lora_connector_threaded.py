import threading
import time
from abc import abstractmethod

import variables
from LoraConnectorAbstract import LoraConnectorAbstract, bytes_to_str, str_to_bytes


class LoraConnectorThreaded(LoraConnectorAbstract):
    def __init__(self, ser_conn):
        super().__init__(ser_conn)

    def execute_command(self, command):
        command = command + '\r\n'
        command = bytes(command, variables.ENCODING)
        self.ser.write(command)

    def receive_messages(self):
        while True:
            if self.ser.in_waiting > 0:
                self.handle_received_line(message=self.ser.readline())

    @abstractmethod
    def handle_received_line(self, message):
        print(message)

    def start_receiving_thread(self):
        t = threading.Thread(target=self.receive_messages)
        t.start()


class LoraConnectorThreadedSyncedResponse(LoraConnectorAbstract):

    COMMAND_SENDED = False

    def __init__(self, ser):
        super(LoraConnectorThreadedSyncedResponse, self).__init__(ser)
        self.t = None

    def execute_command(self, command, verify_response_list=None):
        successful = True
        command = command + '\r\n'
        command = str_to_bytes(command)
        if verify_response_list is not None:
            for expected_response in verify_response_list:
                self.COMMAND_SENDED = True
                self.t.join()
                self.ser.write(command)
                self.t.join()
                response = bytes_to_str(self.ser.readline())
                if response.strip() != expected_response:
                    print('error: could not verify status "{}". Response was: {response}'.format(expected_response,
                                                                                                 response=response))
                    successful = False
                self.start_receiving_thread()
        else:
            self.ser.write(command)
        return successful

    def receive_messages(self):
        while not self.COMMAND_SENDED:
            if self.ser.in_waiting > 0:
                raw_response = self.ser.readline()
                print(raw_response)
                self.handle_received_line(message=bytes_to_str(raw_response))

    @abstractmethod
    def handle_received_line(self, message):
        print(message)

    def start_receiving_thread(self):
        self.t = threading.Thread(target=self.receive_messages)
        self.COMMAND_SENDED = False
        self.t.start()


if __name__ == '__main__':
    lora_threaded = LoraConnectorThreadedSyncedResponse()
    lora_threaded.start_receiving_thread()
    time.sleep(1)
    lora_threaded.execute_command("AT", verify_response_list=['AT,OK'])
