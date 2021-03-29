import socket
import time
import cv2
import threading
import numpy as np

# get streamers's IP address
#streamer_name = socket.gethostname()
#streamer_IP = socket.gethostbyname(streamer_name)

streamer_name = 'JARUS'
streamer_IP = '127.0.0.1'

# define all port numbers
streamer_tcp_port = 60000
streamer_audio_udp_port = 60001
streamer_video_udp_port = 60002
listener_tcp_port = 60003
listener_audio_udp_port = 60004
listener_video_udp_port = 60005

# print streamer info
print("Streamer Name: " + streamer_name)
print("Streamer IP: " + streamer_IP)

# create TCP socket and bind it to streamer's IP and tcp port
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind((streamer_IP, streamer_tcp_port))

listener_tcp_sockets = []
listener_IP_list = []

# function to create the streamer "send list"
def create_streamer_send_list(listener_IP_list):
    send_list = []
    i = 1
    while True:
        index = 2**i-2
        if index < len(listener_IP_list):
            send_list.append(listener_IP_list[index])
        else:
            break
        i += 1
    print(send_list)
    return send_list

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((streamer_IP, streamer_video_udp_port))

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

buf = 0

def video_streamer():
    global buf
    frame = np.zeros((50,50,3))
    cv2.imshow("Streamer",frame)
    while (webcam.isOpened()) and (cv2.getWindowProperty("Streamer", cv2.WND_PROP_VISIBLE) >= 1):
        retval, frame = webcam.read()
        frame = cv2.resize(frame, (50, 50))
        buf = cv2.imencode('.jpg', frame)[1]
        cv2.imshow("Streamer",frame)
        cv2.waitKey(33)
    webcam.release()
    cv2.destroyAllWindows()

def thread_vid_client(udp_video_socket,client_addr):
    global send_list
    global buf
    while True:
        try:
            if client_addr in send_list:
                udp_video_socket.sendto(buf, (client_addr[0],client_addr[1]+2))
        except:
            break

def thread_client_commander(tcp_socket):
    global listener_IP_list
    global send_list
    dl = []
    ping_time = 100
    for i in listener_IP_list:
        dl.append({'ip':i,'ping':ping_time})
    d = {'data':dl}

    for i in range(len(listener_IP_list)):
        try:
            tcp_socket.sendall(str(d).encode(),listener_IP_list[i])
        except:
            del listener_IP_list[i]
            send_list = create_streamer_send_list(listener_IP_list)
    time.sleep(5)

thread_vid_client_ls = []

thread_commnd_client = threading.Thread(target=thread_client_commander,args=(tcp_socket,))
video_thread = threading.Thread(target=video_streamer)
video_thread.start()

tcp_socket.listen(10)
tcp_socket.settimeout(5)

while True:
    try:
        try:
            sock, addr = tcp_socket.accept()
            # store listener IP address and port
            print("New listener:",addr)
            listener_IP_list.append(addr)
            # store tcp client socket
            listener_tcp_sockets.append(sock)
            send_list = create_streamer_send_list(listener_IP_list)
            thread_client = threading.Thread(target=thread_vid_client,args=(udp_video_socket,addr,))
            thread_client.start()
        except:
            pass

    except KeyboardInterrupt:
        print("Streaming terminated")
        break

udp_video_socket.close()
tcp_socket.close()