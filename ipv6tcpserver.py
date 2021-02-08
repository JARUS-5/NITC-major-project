import socket

bind_addr,bind_port = "2405:201:f008:ac36:8623:348d:9204:e1e4",8000

s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
s.bind((bind_addr,bind_port,0,0))

s.listen(1)
client,addr = s.accept()

client.send(b"connected")
m = client.recv(1024)

print(m)

client.close()