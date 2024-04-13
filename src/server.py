import socket
 
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
 
class Listener:
    
    def __init__ (self, ip, port):
        self.port = port
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck.bind((ip, port))

    def listen(self):
        #Nos da un puerto nuevo cada vez. Fuente: https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
        
        # while True:
            data, addr = self.sck.recvfrom(1024) # buffer size is 1024 bytes
            print ("el listener recibió: ", data, "\n")

            w = Worker(addr)
            message = f'{w.port}'
            message_bytes = bytes(f"{message}", 'utf-8')
            self.sck.sendto(message_bytes, (addr[0], addr[1]))
            print("Pasando al worker")
            w.hablar()
            print ("El control volvió al listener")

class Worker:
    def __init__ (self, addressCliente):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck.bind((UDP_IP, 0))
        self.port = self.sck.getsockname()[1]
        self.peer_addr = addressCliente

        
    def hablar(self):
        data, addr = self.sck.recvfrom(1024)
        print ("El worker recibió: ", data, " de: ", addr, "\n")
        message = "Tu nariz contra mis bolas :P"
        message_bytes = bytes(f"{message}", 'utf-8')
        self.sck.sendto(message_bytes, (addr[0], addr[1]))
        print ("Cerrando socket con puerto ", self.port, "\n")

def __main__():
    l = Listener(UDP_IP, UDP_PORT)
    l.listen()

__main__()