import socket
import time

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('127.0.0.1',8888))

m = 'F'.encode()
time.sleep(2)
t = time.time()
s.send(m)
print("Message sent from client at time: ",t)

s.close()