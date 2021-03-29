import socket
import math
import numpy as np
import cv2

# define streamer IP and ports
streamer_IP = "192.168.29.11"
streamer_tcp_port = 60000
streamer_udp_port = 60001

# get listener's IP address
listener_name = socket.gethostname()
listener_IP = socket.gethostbyname(listener_name)

# define listener ports
listener_tcp_port = 60002
listener_audio_udp_port = 60003
listener_video_udp_port = 60004

# print listener info
print("Listener Name: " + listener_name)
print("Listener IP: " + listener_IP)

# define tcp socket and send request to streamer
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind((listener_IP, listener_tcp_port))
tcp_socket.connect((streamer_IP, streamer_tcp_port))

# function to convert a string to a list
''' for example, suppose
listener_IP_list = ['192.168.1.11', '192.168.1.16']
the streamer converts this list to a string using the str() function
str(listener_IP_list) = "['192.168.1.11', '192.168.1.16']"
this string is received by all the listeners through their tcp sockets
we need to convert this string back into a list
'''
def str2list(string):
    list = []
    temp = ''
    flag = False
    for i in string:
        if i == '\'' and flag == False:
            flag = True
        elif i != '\'' and flag == True:
            temp += i
        elif i == '\'' and flag == True:
            flag = False
            list.append(temp)
            temp = ''

    return list

listener_IP_list = str2list(tcp_socket.recv(1024).decode())
num_listener = len(listener_IP_list)
print(len(listener_IP_list))

# find the index of this listener in the list
listener_index = listener_IP_list.index(listener_IP)
print("index = " + str(listener_index))

# function to create the listener's "send list"
# this function might need more testing to check whether it'll work for any possible input
def create_listener_send_list():
    send_list = []
    start = math.floor(math.log2(listener_index + 1)) + 1
    stop = math.floor(math.log2(num_listener - listener_index + 1))      

    for i in range(start, stop + 1):                                     
        send_list.append(2**i + listener_index - 1)

    return send_list

send_list = create_listener_send_list()
print(send_list)

##############################################################

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((listener_IP, listener_video_udp_port))
udp_video_socket.settimeout(5)

while True:
    try:
        buf = udp_video_socket.recv(5*1024)
        jpnp = np.frombuffer(buf, dtype = np.uint8)
        frame = cv2.imdecode(jpnp, cv2.IMREAD_COLOR)
        cv2.imshow("Receiver",frame)
        cv2.waitKey(1)

        for i in send_list:
            udp_video_socket.sendto(buf, (listener_IP_list[i], listener_video_udp_port))

    except OSError:
        print("Server closed")
        break
        
    except KeyboardInterrupt:
        print("Client closed")
        break

cv2.destroyAllWindows()
udp_video_socket.close()
tcp_socket.close()