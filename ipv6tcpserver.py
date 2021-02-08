import socket

bind_addr,bind_port = "2409:4073:105:2beb:67cd:717a:ecab:73d5",8000

s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
s.bind((bind_addr,bind_port,0,0))

s.listen(1)
client,addr = s.accept()

client.send(b"<html><body>connected</body></html>")
m = client.recv(1024)

print(m)
print("got connection")
client.close()