import socket
import time
import cv2
import pyaudio
import tkinter
import PIL.Image, PIL.ImageTk

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

udp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_audio_socket.bind((streamer_IP, streamer_audio_udp_port))

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def callback(in_data, frame_count, time_info, status):
    # sizeof(in_data) = 2081 bytes
    for i in send_list:
        udp_audio_socket.sendto(in_data, (listener_IP_list[i], listener_audio_udp_port))
    return (None, pyaudio.paContinue)

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)

window = tkinter.Tk()
window.title("Streamer")
canvas = tkinter.Canvas(window, width = 480, height = 360)
canvas.pack()

def streamer_video():
    if webcam.isOpened():
        try:
            retval, frame = webcam.read()
            if not retval:
                print("webcam.read() failed")
                return

            frame = cv2.resize(frame, (480, 360)) # sizeof(frame) = 518536
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            buf = cv2.imencode('.jpg', frame)[1]  # sizeof(buf) = ~50000

            for i in send_list:
                udp_video_socket.sendto(buf, (listener_IP_list[i], listener_video_udp_port))
            
            global photo
            photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            canvas.create_image(0, 0, image = photo, anchor = tkinter.NW)
            window.after(50, streamer_video)

        except KeyboardInterrupt:
            print("Streaming terminated")

streamer_video()
num_list_str = tkinter.StringVar()
label = tkinter.Label(window, textvariable = num_list_str)
num_list_str.set("Number of listeners: " + str(num_listener))
label.pack()
window.mainloop()
print("Stopped streaming")

webcam.release()
udp_video_socket.close()
audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
udp_audio_socket.close()
tcp_socket.close()