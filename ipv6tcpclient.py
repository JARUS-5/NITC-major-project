import socket

server_addr,server_port = "2409:4073:105:2beb:67cd:717a:ecab:73d5",8000

c = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
c.connect((server_addr,server_port,0,0))

c.recv(1024)

m = c.recv(1024)
c.send(b"received")
print(m)

c.close()