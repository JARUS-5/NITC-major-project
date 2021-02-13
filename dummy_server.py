# Welcome to PyShine
# In this video server is receiving video from clients.
# Lets import the libraries
import socket, cv2, pickle, struct
import imutils
import threading
import pyshine as ps # pip install pyshine
import pyaudio
import sys
from multiprocessing import Process

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Video server
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)
socket_address_audio=(host_ip,8080)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(socket_address)
server_socket.listen(1)
print("Listening at",socket_address)
audserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Audio server
audserversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
audserversocket.bind(socket_address_audio)
audserversocket.listen(5)
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

def vid_client(addr,client_socket):
    try:
        print('CLIENT {} CONNECTED!'.format(addr))
        if client_socket: # if a client socket exists
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4*1024) # 4K
                    if not packet: break
                    data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0] 
                while len(data) < msg_size:
                    data += client_socket.recv(4*1024)
                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)
                text  =  f"CLIENT: {addr}"
                frame =  ps.putBText(frame,text,10,10,vspace=10,hspace=1,font_scale=0.7, 						background_RGB=(255,0,0),text_RGB=(255,250,250))
                cv2.imshow(f"FROM {addr}",frame)
                key = cv2.waitKey(1) & 0xFF
                if key  == ord('q'):
                    break
            client_socket.close()
            print('Shutting down')
    except Exception as e:
        print(f"CLIENT {addr} DISCONNECTED")
        pass
def aud_client(audio_address,audio_client):
    try:
        print('AUDIO CLIENT {} CONNECTED!'.format(audio_address))
        if audio_client:
            while True:
                audio_data=audserversocket.recv(CHUNK)
                stream.write(audio_data)
    except KeyboardInterrupt:
        print(f"Disconnecting AUDIO from client {audio_address}")
        audio_client.close()
        stream.close()
        audio.terminate()
def multiprocess(addr,client_socket,audio_address,audio_client):
    process_1=Process(target=vid_client(addr,client_socket)) #Video process
    process_2=Process(target=aud_client(audio_address,audio_client)) #Audio process
    process_2.start()
    process_1.start()

while True:
    client_socket,addr = server_socket.accept() #Getting video client and video address
    audio_client, audio_address=audserversocket.accept() #Getting audio client and audio address
    print(audio_client,audio_address)
    thread = threading.Thread(target=multiprocess, args=(addr,client_socket,audio_address,audio_client))
    thread.start()
    print("TOTAL CLIENTS ",threading.activeCount() - 1)