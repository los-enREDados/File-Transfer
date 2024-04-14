import sys
import socket
# import struct

#    DIR.archivo
from lib.SocketRDT import SocketRDT
import lib.constants

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
 
class Listener:
    
    def __init__ (self, ip, port):
        # self.port = port
        # self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sck.bind((ip, port))
        self.recieveSocket = SocketRDT(lib.constants.TIPODEPROTOCOLO,
                                       (0,0), ip, port)

    def listen(self):
        # data, addr = self.sck.recvfrom(1024) # buffer size is 1024 bytes

        addr = self.recieveSocket.acceptConnection()

        # self.socketListen()
        # print (f"el listener recibió: {data} de la direccion {addr}")
        # print(f"JAMON JAMON {data[0:4]}")
        
        # seqNum = struct.unpack("I", data[0:4])

        # print(f"QUESO QUESO {seqNum}")
        # print(type(seqNum))

        w = Worker(addr, UDP_IP)
        w.hablar()

class Worker:
    def __init__ (self, addressCliente, myIP):
        self.socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, addressCliente, myIP)

        self.socketRDT.syncAck()

        print(f"Creo un worker con Puerto: {self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA]}")
        
    def hablar(self):
        data = self.socketRDT.receive_all()
        print ("El worker recibió: ", data, " de: ", self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA], "\n")

        message = data.upper()
        message_bytes = bytes(f"{message}", 'utf-8')

        self.socketRDT.sendall(message_bytes)

def __main__():
    if lib.constants.TIPODEPROTOCOLO != "SW" and lib.constants.TIPODEPROTOCOLO != "SR":
        sys.exit(f'''
\033[91mERROR\033[0m: Tipo de protocolo desconocido: {lib.constants.TIPODEPROTOCOLO}''')

    l = Listener(UDP_IP, UDP_PORT)
    l.listen()

__main__()
