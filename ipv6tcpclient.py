import socket

server_addr,server_port = "2405:201:f008:ac36:8623:348d:9204:e1e4",8000

c = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
c.connect((server_addr,server_port,0,0))

c.recv(1024)

m = c.recv(1024)
c.send(b"received")
print(m)

c.close()