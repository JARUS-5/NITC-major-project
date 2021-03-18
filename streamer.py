import socket
import time
import cv2
import threading

# get streamers's IP address
streamer_name = socket.gethostname()
streamer_IP = socket.gethostbyname(streamer_name)

# define all port numbers
streamer_tcp_port = 60000
streamer_audio_udp_port = 60001
streamer_video_udp_port = 60005
listener_tcp_port = 60002
listener_audio_udp_port = 60003
listener_video_udp_port = 60004

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
def create_streamer_send_list(num_listener):
    send_list = []
    i = 1
    while True:
        index = 2**i-2
        if index < num_listener:
            send_list.append(index)
        else:
            break
        i += 1
    return send_list

####################################################################

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((streamer_IP, streamer_video_udp_port))

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

buf = 0

def video_streamer():
    global buf
    while webcam.isOpened():
        retval, frame = webcam.read()
        frame = cv2.resize(frame, (50, 50))
        buf = cv2.imencode('.jpg', frame)[1]

        #for i in send_list:
        #    udp_video_socket.sendto(buf, (ip, listener_video_udp_port))
        cv2.imshow("Streamer",frame)
        cv2.waitKey(33)

def thread_client(udp_video_socket,client_sock,client_ip):
    global send_list
    global buf
    while True:
        try:
            if client_ip in send_list:
                udp_video_socket.sendto(buf, (client_ip, 60004))
        except:
            break

thread_client_ls = []
video_thread = threading.Thread(target=video_streamer)
video_thread.start()

while True:
    try:
        tcp_socket.listen()
        sock, addr = tcp_socket.accept()
        # store listener IP address
        listener_IP_list.append(addr[0])
        # store tcp client socket
        listener_tcp_sockets.append(sock)
        send_list = create_streamer_send_list(len(listener_IP_list))
        #thread_client_ls.append(threading.Thread(target=thread_client,args=(udp_video_socket,client_sock,client_ip,)))
        #thread_client_ls[-1].start()

    except KeyboardInterrupt:
        print("Streaming terminated")
        break

webcam.release()
cv2.destroyAllWindows()
udp_video_socket.close()
tcp_socket.close()

'''
# set number of listeners
num_listener = 2

# accept connections from listeners
for i in range(num_listener):
    tcp_socket.listen()
    sock, addr = tcp_socket.accept()
    # store listener IP address
    listener_IP_list.append(addr[0])
    # store tcp client socket
    listener_tcp_sockets.append(sock)

# use client sockets to send all listener IPs to all listeners
for sock in listener_tcp_sockets:
    sock.sendall(str(listener_IP_list).encode())

# function to create the streamer "send list"
def create_streamer_send_list(num_listener):
    send_list = []
    i = 1
    while True:
        index = 2**i-2
        if index < num_listener:
            send_list.append(index)
        else:
            break
        i += 1
    return send_list

send_list = create_streamer_send_list(num_listener)
print(send_list)

# wait for 1 seconds so the listeners have to time to prepare for communication
time.sleep(1)

####################################################################

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((streamer_IP, streamer_video_udp_port))

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while webcam.isOpened():
    try:
        retval, frame = webcam.read()
        frame = cv2.resize(frame, (50, 50))
        buf = cv2.imencode('.jpg', frame)[1]

        for i in send_list:
            udp_video_socket.sendto(buf, (listener_IP_list[i], listener_video_udp_port))
        cv2.imshow("Streamer",frame)
        cv2.waitKey(33)

    except KeyboardInterrupt:
        print("Streaming terminated")
        break

webcam.release()
cv2.destroyAllWindows()
udp_video_socket.close()
tcp_socket.close()
'''