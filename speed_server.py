import socket
import time

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

s.bind(('192.168.29.11',8888))
s.sendto(b'hi',('8.8.8.8',8888))
while True:
    data = s.recvfrom(1024)
    t = time.time()
    print(data)
    print("Message received at time: ",t)