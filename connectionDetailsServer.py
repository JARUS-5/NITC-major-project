import socket

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

s.bind(('0.0.0.0',8000))

while True:
    client_msg = s.recvfrom(1024)
    print(client_msg)