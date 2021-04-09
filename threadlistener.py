import socket, time, json, threading, sys
import numpy as np
import cv2
import pyaudio
import tkinter
import PIL.Image, PIL.ImageTk

#------------------CONSTANTS---------------------

APP_STATE = True
listener_IP_list = []
send_list = []

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 1024

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

# print listener info
print("Listener Name: " + listener_name)
print("Listener IP: " + listener_IP)

#------------------------------------------------

#----------------FUNCTIONS-----------------------

def callback(in_data, frame_count, time_info, status):
    global udp_audio_socket, send_list
    try:
        data = udp_audio_socket.recv(2500)
        for i in send_list:
            udp_audio_socket.sendto(data, (listener_IP_list[i], listener_audio_udp_port))
        return (data, pyaudio.paContinue)

    except socket.timeout:
        return (b'0', pyaudio.paComplete)

def video_getter():
    global buf, photo, udp_video_socket
    try:
        buf =  udp_video_socket.recv(70*1024) # sizeof(buf) = ~50000
        jpnp = np.frombuffer(buf, dtype = np.uint8)
        frame = cv2.imdecode(jpnp, cv2.IMREAD_COLOR)

        photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        canvas.create_image(0, 0, image = photo, anchor = tkinter.NW)
        window.after(50, video_getter)

    except KeyboardInterrupt:
        print("Streaming terminated")
    
    #except:
    #    print("Error encountered while streaming video")

def create_streamer_send_list(listener_IP_list):
    global listener_IP, listener_tcp_port, APP_STATE
    pos = listener_IP_list.index([listener_IP,listener_tcp_port])
    i = pos + 1
    send_list = []
    while APP_STATE:
        index = 2**i-1+pos
        if index < len(listener_IP_list):
            send_list.append(listener_IP_list[index])
        else:
            break
        i += 1
    return send_list

def thread_vid_client(udp_video_send_socket):
    global send_list, buf, APP_STATE
    while APP_STATE:
        try:
            for client_addr in send_list:
                udp_video_send_socket.sendto(buf, (client_addr[0],client_addr[1]+2))
        except:
            break

def UI_update():
    global num_list_str,send_list_str
    global listener_IP_list, send_list

    num_list_str.set("Number of listeners: " + str(len(listener_IP_list)) 
    + "\nListener IP addresses\n" + str(listener_IP_list).lstrip('[').rstrip(']').replace(',','\n'))
    send_list_str.set("send list\n " + str(send_list).lstrip('[').rstrip(']').replace(',','\n'))

def server_commands(tcp_socket):
    global APP_STATE, listener_IP_list, send_list

    while APP_STATE:
        try:
            r = tcp_socket.recv(10*1024)
            tcp_socket.send(r)
            listener_IP_list = json.loads(r.decode())
            send_list = create_streamer_send_list(listener_IP_list)
        except:
            break
        UI_update()

def Stop_Services(event):
    try:
        window.destroy()
    except:
        print("Window already closed.")

    APP_STATE = False
    audio_stream.stop_stream()
    audio_stream.close()
    audio.terminate()
    udp_video_socket.close()
    tcp_socket.close()

    print("Streaming services stopped")
    sys.exit()

#------------------------------------------------

#--------------SOCKETS AND THREADING-------------

# define tcp socket and send request to streamer
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind((listener_IP, listener_tcp_port))
tcp_socket.connect((streamer_IP, streamer_tcp_port))
tcp_socket.settimeout(20)

udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((listener_IP, listener_video_udp_port))
udp_video_socket.settimeout(10)

udp_video_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# UDP Audio socket
udp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_audio_socket.bind((listener_IP, listener_audio_udp_port))

# Pyaudio
audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=callback)
audio_stream.start_stream()

# Tkinter window
window = tkinter.Tk()
window.title("Listener")

# Frame 1
frame1 = tkinter.Frame(master=window)
canvas = tkinter.Canvas(window, width = 480, height = 360)
canvas.pack(side=tkinter.LEFT)

# Frame 2
frame2 = tkinter.Frame(master=frame1,width=200,height= 360)

# Listener IP list on tk
num_list_str = tkinter.StringVar()
label1 = tkinter.Label(frame2, textvariable = num_list_str)
num_list_str.set("Number of listeners: " + str(len(listener_IP_list)) 
                + "\nListener list: " + str(listener_IP_list))
label1.pack(side=tkinter.TOP,fill=tkinter.BOTH)

# send list on tk
send_list_str = tkinter.StringVar()
label2 = tkinter.Label(frame2, textvariable = send_list_str)
send_list_str.set("send list: " + str(send_list))
label2.pack(side=tkinter.TOP,fill=tkinter.BOTH,expand=True)

frame2.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=True)
frame1.pack()

# frame 3
frame3 = tkinter.Frame(window)

button = tkinter.Button(master=frame3,text="Stop",width=10,height=4,bg="red",fg="white")
button.bind("<Button-1>",Stop_Services)
button.pack(side=tkinter.BOTTOM)

frame3.pack()

# Video thread
video_getter()

thread_server_commands = threading.Thread(target=server_commands,args=(tcp_socket,),daemon=True)
thread_server_commands.start()

tvc = threading.Thread(target=thread_vid_client,args=(udp_video_send_socket,),daemon=True)
tvc.start()

window.mainloop()
Stop_Services('dummy')