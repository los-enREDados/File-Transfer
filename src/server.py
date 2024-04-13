import socket
 
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

class Listener:
    
    def __init__ (self, port):
        self.port = port
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck.bind((UDP_IP, UDP_PORT))

    def listen(self):
        #Nos da un puerto nuevo cada vez. Fuente: https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
        
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            nuevoWorker(addres)

            # nuevoCliente = SocketRDT(addr)
            # nuevoCliente. 


#           nuevoSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#           nuevoSocket.
            # socket.bind((UDP_IP, 0)) 
        
            # nuevoSocket = socket.socket(socket.AF_INET, # Internet
            #                 socket.SOCK_DGRAM) # UDP
            
            # sock.bind((UDP_IP, UDP_PORT))

            w = Worker(addr)
            sock.sendall("Habla por acá papi", addr, "\n")
            w.hablar()


            # nuevoCliente = SocketRDT(addr)
            # print("received message: %s" % data)
            # #print("received addres: %s" % addr)
            # print(addr)

class Worker:
    def __init__ (self, addressCliente):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck.bind((UDP_IP, 0))
        self.port = self.sck.getsockname()[1]

        # self.comunicacionCliente = SocketRDT(addressCliente)
        
    def hablar(self):
        self.sck.sendall("Hola capo, te estás comunicando con el worker a traves de: ", self.port, "\n")
