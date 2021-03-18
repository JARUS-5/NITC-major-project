import socket

server_addr,server_port = "",8000

c = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
c.connect((server_addr,server_port,0,0))

m = c.recv(1024)
c.send(b"received")
print(m)

c.close()