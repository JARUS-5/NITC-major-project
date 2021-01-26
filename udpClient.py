'''
import zmq

bind_addr = 'udp://127.0.0.1:8001'
server_addr = 'udp://127.0.0.1:8000'

context = zmq.Context()
#socket = context.socket(zmq.DISH)

socket.bind(bind_addr)
socket.connect(server_addr)

while True:
    a = socket.recv()
    print(a)

'''

import socket
import time

bind_addr = '127.0.0.1'
server_addr = '127.0.0.1'

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((bind_addr,8001))

s.connect((server_addr,8000))

while True:
    s.send(b'Working')
    message = s.recv(1024)
    time.sleep(5)
    print(message)