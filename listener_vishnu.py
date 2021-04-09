import socket
import math
import numpy as np
import cv2
import pyaudio
import tkinter
import PIL.Image, PIL.ImageTk

# define streamer IP and ports
streamer_IP = "192.168.1.11"
streamer_tcp_port = 60000

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
        if i < num_listener:
            send_list.append(2**i + listener_index - 1)

    return send_list

send_list = create_listener_send_list()
print(send_list)

##############################################################

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((listener_IP, listener_video_udp_port))
udp_video_socket.settimeout(3)

udp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_audio_socket.bind((listener_IP, listener_audio_udp_port))
udp_audio_socket.settimeout(3)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def callback(in_data, frame_count, time_info, status):
    try:
        data = udp_audio_socket.recv(2500)
        for i in send_list:
            udp_audio_socket.sendto(data, (listener_IP_list[i], listener_audio_udp_port))
        return (data, pyaudio.paContinue)

    except socket.timeout:
        return (b'0', pyaudio.paComplete)

audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=callback)
audio_stream.start_stream()

window = tkinter.Tk()
window.title("Listener")
canvas = tkinter.Canvas(window, width = 480, height = 360)
canvas.pack()

def listener_video():
    try:
        buf = udp_video_socket.recv(70*1024)
        jpnp = np.frombuffer(buf, dtype = np.uint8)
        frame = cv2.imdecode(jpnp, cv2.IMREAD_COLOR)

        for i in send_list:
            udp_video_socket.sendto(buf, (listener_IP_list[i], listener_video_udp_port))

        global photo 
        photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        canvas.create_image(0, 0, image = photo, anchor = tkinter.NW)
        window.after(10, listener_video)

    except socket.timeout:
        print("Server closed")
        window.destroy()
        
    except KeyboardInterrupt:
        print("Client closed")
        window.destroy()

def on_closing():
    print("Client closed")
    window.destroy()

listener_video()
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()

audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
udp_audio_socket.close()
udp_video_socket.close()
tcp_socket.close()