import threading
import time

import main


class Messenger:
    ENCODING = 'utf-8'

    def __init__(self, lora_utility):
        self.lora_utility = lora_utility

    def start_receiving_messages(self):
        while True:
            raw_res = self.lora_utility.wait_for_message()
            if raw_res is not None:
                answer_as_list = main.convert_raw_answer_to_list()
                print('got message from {sender} with length {length}: {message}'.format(sender=answer_as_list[1],
                                                                                         length=answer_as_list[2],
                                                                                         message=answer_as_list[3]))

    def read_from_cli_and_send_message(self):
        while True:

            value = input("enter string to send message:\n")
            self.lora_utility.close_connection()
            # self.lora_utility.send_message(value)

    def start_message_receiving_thread(self):
        while True:
            self.lora_utility.open_connection()
            t = threading.Thread(target=self.start_receiving_messages)
            t.start()

            value = input("enter string to send message:\n")
            self.lora_utility.close_connection()
            t.join()
            time.sleep(2)

            self.lora_utility.open_connection()

            self.lora_utility.send_message(value)
            self.lora_utility.close_connection()

            self.read_from_cli_and_send_message()


if __name__ == '__main__':
    lora_conn = main.LoraConnector()
    # lora_conn.config_module()

    # response = lora_conn.send_message('ja', wait_for_answer=True)
    #
    # while True:
    #     lora_conn.wait_for_message()

    messenger = Messenger(lora_conn)
    messenger.start_message_receiving_thread()
    # messenger.start_receiving_messages()