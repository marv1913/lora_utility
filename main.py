import serial
import time

class LoraConnecter():
    
    def __init__(self, com_port='/dev/ttyS0', baudrate=115200):
        self.com_port = com_port
        self.baudrate = baudrate
        
    def execute_command(self, command):
        with serial.Serial(self.com_port, self.baudrate, timeout=1) as ser:
            command = command + '\n'
            command = bytes(command, 'utf-8')
            ser.write(command)
            res = ser.readline()
            return res
    
    def wait_for_message(self):
        with serial.Serial(self.com_port, self.baudrate) as ser:
            return ser.readline()
        
    def send_message(self, message):
        print(self.execute_command('AT+SEND={}'.format(str(len(message)))))
        # ToDo clarify why At+SEND also defines the count of bytes which are received
        return self.execute_command(message)
        
        
if __name__ == '__main__':
    lora_conn = LoraConnecter()
    print(lora_conn.send_message('hello world'))
    time.sleep(1)
    print(lora_conn.send_message('hello world'))
    time.sleep(1)
    print(lora_conn.send_message('hello world'))  
    #print(lora_conn.wait_for_message())
