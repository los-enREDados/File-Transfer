import socket

class SocketRDT:
    def __init__(self, tipo, peerAddr, myIP):
        # Este socket representa el socket que yo voy a usar de OUTPUT.
        # Si a mi me quieren hablar. Yo tengo que bindear este socket
        # Si yo quiero hablar con alguien, uso la direccion para hablar
        self.skt = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        
        # Cuando bind tiene un 0 de segundo argumento nos da un puerto
        # nuevo cada vez. Fuente: https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
        # ATTENTION: Necesitamos bindearlo siempre porque tanto cliente
        # como servidor van a enviar y recibir cosas.
        self.skt.bind((myIP, 0))

        # ATTENTION: No se si hace falta guardar "mi propio address"
        # Lo pongo por si lo llegamos a necesitar
        myPort = self.skt.getsockname()[1]
        self.myAddress = (myIP, myPort)

        self.peerAddr = peerAddr

        self.tipo = tipo

    def sendall(self, tipo):
        if tipo == "SW":
            self._sendall_stop_and_wait()
        else:
            self._sendall_selective()
        return

    def receive_all(self, tipo):
        if tipo == "SW":
            self._receive_stop_and_wait()
        else:
            self._receive_selective()
        return

    def shutdown(self, tipo):
        return

    def _sendall_stop_and_wait(self,):
        pass
    def _sendall_selective(self,):
        pass

    def _receive_stop_and_wait(self,):
        pass

    def _receive_selective(self,):
        pass
