import socket
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--bind", help="Your machine ip address",type=str)
parser.add_argument("--peer", help="Address of machine you are going to connect",type=str)
args = parser.parse_args()

bind_addr = args.bind
peer_addr = args.peer

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((bind_addr,8000))

print("Binded to",bind_addr,"at port 8000")

while True:
    s.sendto(b'Works',(peer_addr,8000))
    s.settimeout(1)
    try:
        message = s.recvfrom(1024)
        print(message)
    except:
        continue
    # time.sleep(1)