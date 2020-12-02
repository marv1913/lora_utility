import serial
import time

class LoraConnecter():

    CONFIG_COMMAND_LIST = ['AT+CFG=433500000,5,6,12,4,1,0,0,0,0,3000,8,4', 'AT+ADDR=0137', 'AT+DEST=FFFF', 'AT+RX']
    SAVE_COMMAND = 'AT+SAVE'
    ENCODING = 'utf-8'

    def __init__(self, com_port='/dev/ttyS0', baudrate=115200):
        self.com_port = com_port
        self.baudrate = baudrate
        
    def execute_command(self, command, count_expected_responses=1):
        with serial.Serial(self.com_port, self.baudrate, timeout=1) as ser:
            res_list = []
            print('execute command: {}'.format(command))
            command = command + '\r\n'
            command = bytes(command, self.ENCODING)
            ser.write(command)
            if count_expected_responses == 1:
                res = ser.readline()
                print('response: {}'.format(res.decode(self.ENCODING)))
                return res
            while count_expected_responses > 0:
                res = ser.readline()
                if len(res) != 0:
                    print('response: {}'.format(res.decode(self.ENCODING)))
                    res_list.append(res)
                    count_expected_responses -= 1
            return res_list
    
    def wait_for_message(self):
        with serial.Serial(self.com_port, self.baudrate) as ser:
            return ser.readline()
        
    def send_message(self, message, wait_for_answer=False):
        # print(self.execute_command('AT+SEND={}'.format(str(len(message)))))
        # ToDo clarify why At+SEND also defines the count of bytes which are received
        self.execute_command('AT+SEND={}'.format(10))
        res = self.execute_command(message, count_expected_responses=2)
        if wait_for_answer:
            return self.wait_for_message(), res
        return res

    def config_module(self, save_config=True):
        for command in self.CONFIG_COMMAND_LIST:
            self.execute_command(command)
        if save_config:
            self.execute_command(self.SAVE_COMMAND)
        
if __name__ == '__main__':
    lora_conn = LoraConnecter()
    # lora_conn.config_module()

    response = lora_conn.send_message('hello world', wait_for_answer=True)
    print(response[0])