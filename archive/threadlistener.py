import socket
import time
import cv2
import threading
import numpy as np
import json

APP_STATE = True
listener_IP_list = []
send_list = []

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

def create_streamer_send_list(listener_IP_list):
    global listener_IP, listener_tcp_port, APP_STATE
    pos = listener_IP_list.index([listener_IP,listener_tcp_port])
    i = pos + 1
    print("pos:",pos)
    send_list = []
    while APP_STATE:
        index = 2**i-1+pos
        if index < len(listener_IP_list):
            send_list.append(listener_IP_list[index])
        else:
            break
        i += 1
    print("send list:",send_list)
    return send_list

def thread_vid_client(udp_video_send_socket):
    global send_list, buf, APP_STATE
    while APP_STATE:
        try:
            for client_addr in send_list:
                udp_video_send_socket.sendto(buf, (client_addr[0],client_addr[1]+2))
        except:
            break

def server_commands(tcp_socket):
    global APP_STATE, listener_IP_list, send_list

    while APP_STATE:
        try:
            r = tcp_socket.recv(1024).decode()
            listener_IP_list = json.loads(r)
            print("Listener list:",listener_IP_list)
            send_list = create_streamer_send_list(listener_IP_list)
        except:
            break

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((listener_IP, listener_video_udp_port))
udp_video_socket.settimeout(5)

udp_video_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

thread_server_commands = threading.Thread(target=server_commands,args=(tcp_socket,))
thread_server_commands.start()

tvc = threading.Thread(target=thread_vid_client,args=(udp_video_send_socket,))
tvc.start()

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
        APP_STATE = False
        break

    except:
        print("Streaming Ended")
        APP_STATE = False
        break

APP_STATE = False
cv2.destroyAllWindows()
udp_video_socket.close()
udp_video_send_socket.close()
tcp_socket.close()