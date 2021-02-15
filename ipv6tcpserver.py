import socket

bind_addr,bind_port = "",8000

s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
s.bind((bind_addr,bind_port,0,0))

s.listen(1)
client,addr = s.accept()

client.send(b"server connected")
m = client.recv(1024)

print(m)
print("got connection")
client.close()