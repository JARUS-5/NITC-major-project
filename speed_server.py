import socket
import time

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(('127.0.0.1',8888))

s.listen(1)
client,addr = s.accept()

data = client.recv(1024)
t = time.time()

print(data.decode('utf-8'))
print("Message received at time: ",t)