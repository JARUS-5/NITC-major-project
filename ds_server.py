import socket
import time
import argparse
import _thread
import concurrent.futures

# Argument parser. Pass port as arg
parser = argparse.ArgumentParser()
parser.add_argument("--server_port", help="server ports",type=int)
args = parser.parse_args()
print("Server port:", args.server_port)

#-------------Server----------------------------
bind_ip = '127.0.0.1'
bind_port = args.server_port

try:
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((bind_ip,bind_port))
    print("Server started successfully at {}:{}".format(bind_ip,bind_port))
except:
    print("Server not started")

def ping(c):
    message = ('PING:'+'A'*1000).encode()
    ts = time.time()
    c.send(message)
    r_message = c.recv(1024).decode('utf-8')
    username = r_message.split(':')[0]
    tr = time.time()
    tft = (tr - ts)*1000
    print(tft)
    return (username,c,c.getpeername(),tft)

class Distribute_Server:
    def __init__(self):
        self.clients_dict = {}
        self.templs = []
        self.tempcn = 'a'
        self.message = ('MESSAGE:'+'A'*1000).encode()
    
    def add_clients(self,ctup):
        u,c,cadp,t = ctup
        print("Client added :",cadp)
        self.tempcn = cadp[0]+":"+str(cadp[1])
        self.templs = [c,cadp,t]
        self.clients_dict[u] = self.templs
    
    def sort_clients(self):
        self.clients_dict = dict(sorted(self.clients_dict.items(), key=lambda item: item[1][-1]))
    
    def show_table(self):
        print(self.clients_dict)
    
    def send_table(self):
        table = ('TABLE:'+str(self.clients_dict)).encode()
        for i in self.clients_dict:
            self.clients_dict[i][0].send(table)
        print('Table sent')
    
    def send_message(self):
        i = 1
        pos = 1
        users = list(self.clients_dict)
        while(pos<=len(users)):
            sendto = self.clients_dict[users[pos-1]]
            sendto[0].send(self.message)
            i = i+1
            pos = ((2**i)-1)

ds = Distribute_Server()

def run_server(ds,s):
    while True:
        s.listen(10)
        client,addr = s.accept()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(ping, client)
            ds.add_clients(future.result())

_thread.start_new_thread(run_server,(ds,s,))

while True:
    time.sleep(10)
    for i in ds.clients_dict:
        r = ping(ds.clients_dict[i][0])
        ds.clients_dict[i][-1] = r[-1]
    ds.sort_clients()
    ds.show_table()
    ds.send_table()
    ds.send_message()

s.close()