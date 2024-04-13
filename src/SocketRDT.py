from socket import *
# Con el que estoy hablando

class SocketRDT:
    def __init__(self, tipo, addrPeer, myIP):
        # Este socket representa el socket que yo voy a usar de OUTPUT.
        # Si a mi me quieren hablar. Yo tengo que bindear este socket
        # Si yo quiero hablar con alguien, uso la direccion para hablar
        self.skt = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        
        self.skt.bind((UDP_IP, 0))


        self.IPPeer = addrPeer[0]
        self.PuertoPeer = addrPeer[1]

        self.IPmy = myIP
        self.socketMIne = sock.getsockname()[1]

        self.tipo = tipo

    def sendall(self, tipo):
        if tipo == "SW":
            sendall_stop_and_wait()
        else:
            sendall_selective()
        return

    def receive_all(self, tipo):
        if tipo == "SW":
            receive_stop_and_wait()
        else:
            receive_selective()
        return

    def shutdown(self, tipo):
        return

# Socket Servidor    <- Socket Cliente 1
#       ^
#       |
#   Socket Cliente 2