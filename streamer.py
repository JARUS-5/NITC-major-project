import socket, time, json, threading, sys
import cv2
import pyaudio
import tkinter
import PIL.Image, PIL.ImageTk

#------------------CONSTANTS---------------------

APP_STATE = True
streamer_name = 'JARUS'
streamer_IP = '127.0.0.1'

# get streamers's IP address
#streamer_name = socket.gethostname()
#streamer_IP = socket.gethostbyname(streamer_name)

# define all port numbers
streamer_tcp_port = 60000
streamer_audio_udp_port = 60001
streamer_video_udp_port = 60002

# audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 1024

listener_tcp_sockets = []
listener_IP_list = []
send_list = []
thread_vid_client_ls = []

buf = 0

#------------------------------------------------

# print streamer info
print("Streamer Name: " + streamer_name)
print("Streamer IP: " + streamer_IP)

#----------------FUNCTIONS-----------------------

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    # sizeof(in_data) = 2081 bytes
    global send_list,listener_IP_list, udp_audio_socket
    for i in send_list:
        udp_audio_socket.sendto(in_data, (i[0], i[1]+1))
    return (None, pyaudio.paContinue)

# function to create the streamer "send list"
def create_streamer_send_list(listener_IP_list):
    global APP_STATE
    send_list = []
    i = 1
    while APP_STATE:
        index = 2**i-2
        if index < len(listener_IP_list):
            send_list.append(listener_IP_list[index])
        else:
            break
        i += 1
    return send_list

# Function which creates video packets(buf) and
# opens image window
def video_streamer():
    global buf, webcam, photo
    try:
        if webcam.isOpened():
            retval, frame = webcam.read()
            if not retval:
                print("webcam.read() failed")
                return

            frame = cv2.resize(frame, (480, 360)) # sizeof(frame) = 518536
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            buf = cv2.imencode('.jpg', frame)[1]  # sizeof(buf) = ~50000

            photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            canvas.create_image(0, 0, image = photo, anchor = tkinter.NW)
            window.after(50, video_streamer)

    except KeyboardInterrupt:
        print("Streaming terminated")
    
    except:
        print("Error encountered while streaming video")

# Function which sends packets to the clients
def thread_vid_client(udp_video_socket,client_addr):
    global send_list, buf, APP_STATE
    while APP_STATE:
        try:
            if client_addr in send_list:
                udp_video_socket.sendto(buf, (client_addr[0],client_addr[1]+2))
        except:
            break

def thread_client_commander():
    global listener_tcp_sockets
    global listener_IP_list
    global send_list, APP_STATE
    while APP_STATE:
        dl = []
        for i in range(len(listener_tcp_sockets)-1,-1,-1):
            try:
                mssg = '{}'.format(json.dumps(listener_IP_list))
                listener_tcp_sockets[i].send(mssg.encode())
            except:
                del listener_IP_list[i]
                del listener_tcp_sockets[i]
                send_list = create_streamer_send_list(listener_IP_list)
        UI_update()
        time.sleep(5)

def client_threader(tcp_socket):
    global listener_tcp_sockets
    global listener_IP_list
    global send_list, APP_STATE

    tcp_socket.listen(10)
    tcp_socket.settimeout(5)
    while APP_STATE:
        try:
            try:
                sock, addr = tcp_socket.accept()
                print("New listener:",addr)
                # store listener IP address and port
                listener_IP_list.append(addr)
                # store tcp client socket
                listener_tcp_sockets.append(sock)
                send_list = create_streamer_send_list(listener_IP_list)
                thread_client = threading.Thread(target=thread_vid_client,args=(udp_video_socket,addr,))
                thread_client.start()
                UI_update()
            except:
                pass

        except:
            print("Streaming terminated")
            APP_STATE = False
            break

def UI_update():
    global num_list_str,send_list_str
    global listener_IP_list, send_list

    num_list_str.set("Number of listeners: " + str(len(listener_IP_list)) 
    + "\nListener IP addresses\n" + str(listener_IP_list).lstrip('[').rstrip(']').replace(',','\n'))
    send_list_str.set("send list\n " + str(send_list).lstrip('[').rstrip(']').replace(',','\n'))

def Stop_Services(event):
    try:
        window.destroy()
    except:
        print("Window already closed.")

    APP_STATE = False
    webcam.release()
    audio_stream.stop_stream()
    audio_stream.close()
    audio.terminate()
    udp_video_socket.close()
    tcp_socket.close()

    print("Streaming services stopped")
    sys.exit()

#------------------------------------------------

#--------------SOCKETS AND THREADING-------------

# create TCP socket and bind it to streamer's IP and tcp port
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind((streamer_IP, streamer_tcp_port))

# UDP video socket
udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_socket.bind((streamer_IP, streamer_video_udp_port))

# UDP Audio socket
udp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_audio_socket.bind((streamer_IP, streamer_audio_udp_port))

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Audio
audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)

# Tkinter window
window = tkinter.Tk()
window.title("Streamer")

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
video_streamer()

# Controller TCP socket
thread_commnd_client = threading.Thread(target=thread_client_commander,daemon=True)
thread_commnd_client.start()

client_thread = threading.Thread(target=client_threader,args=(tcp_socket,),daemon=True)
client_thread.start()

window.mainloop()

Stop_Services('dummy')