import socket
import os
from parse import parse
import argparse


SOCKET_HOST = os.getenv('SOCKET_HOST', 'localhost')
SOCKET_PORT = int(os.getenv('SOCKET_PORT', '12345'))
BUFFER_SIZE = 16

class DeviceSerial():
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def write(self, msg):
        buf = msg.encode()
        buf = buf.ljust(BUFFER_SIZE, b'\0')[:BUFFER_SIZE]
        self.sock.sendall(buf)

    def read(self):
        buf = bytearray()
        for _ in range(BUFFER_SIZE):
            buf.extend(self.sock.recv(1))
        buf = buf.decode().rstrip('\0')
        return buf.strip()

class Device():
    def __init__(self, host, port):
        self.serial = DeviceSerial(host, port)

    def check_ready(self):
        ret = self.serial.read()
        return ret == 'READY'

    def ping(self):
        self.serial.write("PING")
        ret = self.serial.read()
        return ret == 'PONG'
    
    def restart(self):
        self.serial.write("RESTART")
        ret = self.serial.read()
        return ret == 'RESTART'

    def run_test(self, case_num):
        self.serial.write("RUN {}".format(case_num))
        ret = self.serial.read()
        if len(ret) == 0:
            # Empty return means we timed out, therefore fail
            return 2
        
        print(ret)
        ret = parse('RESULT {case_num:d} {result:d}', ret)
        return ret['result']
    
    def last_result(self):
        self.serial.write("RESULT")
        ret = self.serial.read()
        ret = parse('RESULT {case_num:d} {result:d}', ret)
        return (ret['case_num'], ret['result'])
    
def main():
    parser = argparse.ArgumentParser(prog='SocketProgrammer', description='')
    parser.add_argument('--host', default=SOCKET_HOST)
    parser.add_argument('-p', '--port', default=SOCKET_PORT, type=int)
    parser.add_argument('-t', '--test', type=int, required=True)
    
    args = parser.parse_args()

    device = Device(args.host, args.port)

    if args.test is not None:
        device.restart()
        device.check_ready()
        result = device.run_test(args.test)
        if result == 0:
            print('PASS')
        elif result == 1:
            print('SKIP')
        elif result == 2:
            print('FAIL')
        else:
            print('UNKNOWN')

if __name__ == '__main__':
    main()