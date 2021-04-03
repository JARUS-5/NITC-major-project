import socket
import time
import cv2
import threading
import numpy as np
import json

# get listener's IP address
#listener_name = socket.gethostname()
#listener_IP = socket.gethostbyname(streamer_name)

listener_name = 'JARUS'
listener_IP = '127.0.0.1'

# define all port numbers
streamer_tcp_port = 60000
streamer_audio_udp_port = 60001
streamer_video_udp_port = 60002
listener_tcp_port = 60003
listener_audio_udp_port = 60004
listener_video_udp_port = 60005

streamer_IP = "127.0.0.1"
streamer_tcp_port = 60000
streamer_udp_port = 60002

# print listener info
print("Listener Name: " + listener_name)
print("Listener IP: " + listener_IP)

# define tcp socket and send request to streamer
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind((listener_IP, listener_tcp_port))
tcp_socket.connect((streamer_IP, streamer_tcp_port))
tcp_socket.settimeout(20)

def server_commands(tcp_socket):
    while True:
        r = tcp_socket.recv(1024).decode().split(':')
        d = json.loads(r[1])
        print(d)

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((listener_IP, listener_video_udp_port))
udp_video_socket.settimeout(5)

thread_server_commands = threading.Thread(target=server_commands,args=(tcp_socket,))
thread_server_commands.start()

frame = np.zeros((480,360,3))
cv2.imshow("Receiver",frame)
while cv2.getWindowProperty("Receiver", cv2.WND_PROP_VISIBLE) >= 1:
    try:
        buf = udp_video_socket.recv(650*1024)
        jpnp = np.frombuffer(buf, dtype = np.uint8)
        frame = cv2.imdecode(jpnp, cv2.IMREAD_COLOR)
        cv2.imshow("Receiver",frame)
        cv2.waitKey(1)

    except KeyboardInterrupt:
        print("Client closed")
        break

    except:
        pass

cv2.destroyAllWindows()
udp_video_socket.close()
tcp_socket.close()