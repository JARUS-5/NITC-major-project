'''
import zmq
import time

bind_addr = 'udp://127.0.0.1:8000'

context = zmq.Context()
#socket = context.socket(zmq.RADIO)

socket.bind(bind_addr)

while True:
    socket.send(b'Working')
    time.sleep(1)

'''

import socket
import time

bind_addr = '127.0.0.1'
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((bind_addr,8000))
while True:
    pack = s.recvfrom(1024)
    message = pack[0]
    client_addr = pack[1]
    s.sendto(b'reply from server',client_addr)
    print(message)