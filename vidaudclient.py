import socket
import cv2
#import threading
import pyaudio
import sys
import numpy as np

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
audio = pyaudio.PyAudio()

vid_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Video server
vid_ip = '127.0.0.1'
vid_port = 9294

aud_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Audio server
aud_ip = '127.0.0.1'
aud_port = 9295

#track_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#track_ip = '127.0.0.1'
#track_port = 9293

try:
    #track_socket.bind((track_ip,track_port))
    vid_socket.bind((vid_ip,vid_port))
    aud_socket.bind((aud_ip,aud_port))
except:
    print("Error in binding socket.")
    sys.exit()

def vid_client(vid_socket):
    print("Starting Video receiver")
    while True:
        #try:
        buf = vid_socket.recv(5*1024)
        jpnp = np.frombuffer(buf,dtype=np.uint8)
        frame = cv2.imdecode(jpnp,cv2.IMREAD_COLOR)
        cv2.imshow("Receiver",frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        #except:
            #print("Problem in video")
            #break

def callback(in_data, frame_count, time_info, status):
    data = aud_socket.recv(5*1024)
    return (data, pyaudio.paContinue)

print("Starting Audio")
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK, stream_callback=callback)
stream.start_stream()
print("Audio started")
vid_client(vid_socket)
print("Video streaming ended")

pflag = 0
while pflag==0:
    try:
        a = 1
    except KeyboardInterrupt:
        vid_socket.close()
        aud_socket.close()
        stream.stop_stream()
        stream.close()
        audio.terminate()
        cv2.destroyAllWindows()
        pflag = 1