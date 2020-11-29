import socket
import time
import argparse
# import _thread
# import concurrent.futures

# Argument parser. Pass port as arg
parser = argparse.ArgumentParser()
#parser.add_argument("ports", nargs='+', help="target server ports",type=int)
parser.add_argument("--username", help="Unique username",type=str)
args = parser.parse_args()
#print("Target server ports:", args.ports)
print("Username:", args.username)

#-------------Server addr-------------------------
server_ip = '127.0.0.1'
server_port = 8000

try:
    c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print("client started successfully")
except:
    print("Client not started")

c.connect((server_ip,server_port))

while True:
    r = c.recv(2048).decode('utf-8').split(':')
    if r[0]=='PING':
        m = (args.username+":"+r[1]).encode()
        c.send(m)
    elif r[0]=='TABLE':
        print(r)
    else:
        print("Message received")