import socket

#    DIR.archivo
from lib.SocketRDT import SocketRDT
import lib.constants

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
 
class Listener:
    
    def __init__ (self, ip, port):
        self.port = port
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck.bind((ip, port))

    def listen(self):
        data, addr = self.sck.recvfrom(1024) # buffer size is 1024 bytes
        print (f"el listener recibió: {data} de la direccion {addr}")

        w = Worker(addr, UDP_IP)
        w.hablar()

class Worker:
    def __init__ (self, addressCliente, myIP):
        self.socketRDT = SocketRDT("SW", addressCliente, myIP)

        self.socketRDT.acceptConnection()
        
    def hablar(self):
        data = self.socketRDT.receive_all()
        print ("El worker recibió: ", data, " de: ", self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA], "\n")

        message = data.upper()
        message_bytes = bytes(f"{message}", 'utf-8')

        self.socketRDT.sendall(message_bytes)

def __main__():
    l = Listener(UDP_IP, UDP_PORT)
    l.listen()

__main__()
