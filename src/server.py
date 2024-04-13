import socket
 
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


# Con el que estoy hablando
class SocketRDT:
    def __init__(self, tipo, addr):
        self.IP = addr[0]
        self.Puerto = addr[1]
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


while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    nuevoCliente = SocketRDT(addr)
    print("received message: %s" % data)
    #print("received addres: %s" % addr)
    print(addr)