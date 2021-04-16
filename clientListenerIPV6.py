import socket, time, json, threading, sys
import numpy as np
import cv2
import pyaudio
import tkinter
import PIL.Image, PIL.ImageTk

#------------------CONSTANTS---------------------

streamer_IP = '127.0.0.1' # default

APP_STATE = True
listener_IP_list = []
send_list = []

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 1024

# get listener's IP address
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
s.connect(('2001:888:2000:d::a2', 80, 0, 0)) # Connect to python server
listener_IP = s.getsockname()[0]
s.close()

# define all port numbers
streamer_tcp_port = 60000
streamer_audio_udp_port = 60001
streamer_video_udp_port = 60002
listener_tcp_port = 60003
listener_audio_udp_port = 60004
listener_video_udp_port = 60005

# print listener info
print("Listener IP: " + listener_IP)

#------------------------------------------------

#---------------CONNECT--------------------------

def Get_streamer_ip():
    global streamer_IP, listener_IP 
    global entry1, entry2, entry3
    global listener_tcp_port
    global listener_audio_udp_port
    global listener_video_udp_port

    streamer_IP = entry1.get()
    listener_tcp_port = int(entry2.get())
    listener_audio_udp_port = listener_tcp_port + 1
    listener_video_udp_port = listener_tcp_port + 2
    listener_IP = entry3.get()
    configure.quit()
    configure.destroy()

# Tkinter window
configure = tkinter.Tk()
configure.title("Let's connect!")

label = tkinter.Label(
    configure,
    text="Enter the IPV4 address of the streamer",
    width=50,
    height=4
)
label.pack()

entry1 = tkinter.Entry(configure)
entry1.pack(pady=(0,10))

debuglabel = tkinter.Label(
    configure,
    text="\nAdvanced settings for debugging",
    width=50,
    height=4
)
debuglabel.pack(pady=(0,5))

iplabel = tkinter.Label(
    configure,
    text="Enter the custom IPV4 address of your client",
    width=50,
    height=4
)
iplabel.pack()

entry3 = tkinter.Entry(configure)
entry3.insert(0,listener_IP)
entry3.pack(pady=(0,10))

portlabel = tkinter.Label(
    configure,
    text="Enter the custom port of your client",
    width=50,
    height=4
)
portlabel.pack()

entry2 = tkinter.Entry(configure)
entry2.insert(0,str(listener_tcp_port))
entry2.pack(pady=(0,10))

buttonst = tkinter.Button(
    master=configure,
    text="Connect",
    width=10,height=4,
    bg="green",fg="white",
    command=Get_streamer_ip)
buttonst.pack(pady=(10,10))

configure.mainloop()

#----------------FUNCTIONS-----------------------

def callback(in_data, frame_count, time_info, status):
    global udp_audio_socket, send_list
    try:
        udp_audio_socket.sendto(b'Hello',(streamer_IP,streamer_audio_udp_port,0,0))
        data = udp_audio_socket.recv(3000)
        for i in send_list:
            udp_audio_socket.sendto(data, (i[0], i[1]+1,0,0))
        return (data, pyaudio.paContinue)

    except socket.timeout:
        return (b'0', pyaudio.paComplete)
    except:
        print("A client connection closed")
        return (b'0', pyaudio.paContinue)

def video_getter():
    global buf, photo, udp_video_socket
    global udp_video_send_socket, send_list
    try:
        udp_video_socket.sendto(b'Hello',(streamer_IP,streamer_video_udp_port,0,0))
        buf =  udp_video_socket.recv(70*1024) # sizeof(buf) = ~50000
        jpnp = np.frombuffer(buf, dtype = np.uint8)
        frame = cv2.imdecode(jpnp, cv2.IMREAD_COLOR)

        photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        canvas.create_image(0, 0, image = photo, anchor = tkinter.NW)

        for client_addr in send_list:
            udp_video_send_socket.sendto(buf, (client_addr[0],client_addr[1]+2,0,0))
        
        window.after(50, video_getter)

    except KeyboardInterrupt:
        print("Streaming terminated")

def create_streamer_send_list(listener_IP_list):
    global listener_IP, listener_tcp_port, APP_STATE
    pos = listener_IP_list.index([listener_IP,listener_tcp_port,0,0])
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
tcp_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM,0)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind((listener_IP, listener_tcp_port,0,0))
tcp_socket.connect((streamer_IP, streamer_tcp_port,0,0))
tcp_socket.settimeout(None)

udp_video_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM,0)
udp_video_socket.bind((listener_IP, listener_video_udp_port,0,0))
udp_video_socket.settimeout(None)
udp_video_socket.sendto(b'Hello',(streamer_IP,streamer_video_udp_port,0,0))

udp_video_send_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM,0)

# UDP Audio socket
udp_audio_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM,0)
udp_audio_socket.bind((listener_IP, listener_audio_udp_port,0,0))
udp_audio_socket.sendto(b'Hello',(streamer_IP,streamer_audio_udp_port,0,0))

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

window.mainloop()
Stop_Services('dummy')