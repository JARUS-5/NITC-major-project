import socket
import cv2
#import threading
import pyaudio
import sys
#from multiprocessing import Process

vid_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Video server
vid_ip = '127.0.0.1'
vid_port = 9291

aud_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #Audio server
aud_ip = '127.0.0.1'
aud_port = 9292

#track_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#track_ip = '127.0.0.1'
#track_port = 9293

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
audio = pyaudio.PyAudio()

try:
    #track_socket.bind((track_ip,track_port))
    vid_socket.bind((vid_ip,vid_port))
    aud_socket.bind((aud_ip,aud_port))
except:
    print("Error in binding socket.")
    sys.exit()

addrs = ['127.0.0.1']
vid_ports = [9294]
aud_ports = [9295]

def vid_client(vid_socket, addrs, ports):
    print("Starting Video streaming")
    camera = True
    if camera == True:
        vid = cv2.VideoCapture(0)
    else:
        vid = cv2.VideoCapture('videos/mario.mp4')
    while (vid.isOpened()):
        try:
            retval, frame = vid.read()
            frame = cv2.resize(frame,(50,50))
            buf = cv2.imencode('.jpg',frame)[1]
            for client in zip(addrs,ports):
                vid_socket.sendto(buf,client)
            cv2.imshow("Streamer",frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        except:
            print("Problem in video")
            break
    vid.release()

def callback(in_data, frame_count, time_info, status):
    for client in zip(addrs,aud_ports):
        aud_socket.sendto(in_data,client)
    return (None, pyaudio.paContinue)

print("Starting Audio streaming")
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
print("Audio streaming started")
vid_client(vid_socket,addrs,vid_ports)
print("Video streaming ended")

Flag = 0
while Flag==0:
    try:
        a = 1
    except KeyboardInterrupt:
        vid_socket.close()
        aud_socket.close()
        stream.stop_stream()
        stream.close()
        audio.terminate()
        cv2.destroyAllWindows()
        Flag = 1