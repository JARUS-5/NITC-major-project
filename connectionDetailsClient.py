import socket

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

s.sendto(b'HEllo',("65.0.179.4",8000))