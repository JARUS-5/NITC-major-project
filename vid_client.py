import socket,cv2, pickle,struct
import pyshine as ps # pip install pyshine
import imutils # pip install imutils
import pyaudio
import time
import select

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 192000
CHUNK = 1024*16

camera = True
if camera == True:
    vid = cv2.VideoCapture(0)
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = socket.gethostbyname(socket.gethostname())#'192.168.1.11' # Here according to your server ip write the address
port = 9999
client_socket.connect((host_ip,port))
audio_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
audio_socket.connect((host_ip,8080))
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
print ("recording...")
if client_socket and audio_socket:
    while (vid.isOpened()):
        try:
            data=stream.read(CHUNK)
            audio_socket.send(data)
            img, frame = vid.read()
            frame = imutils.resize(frame,width=380)
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            client_socket.sendall(message)
            cv2.imshow(f"TO: {host_ip}",frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                client_socket.close()
                audio_socket.close()
                # stop Recording
                stream.stop_stream()
                stream.close()
                audio.terminate()
        except:
            print('VIDEO FINISHED!')
            break