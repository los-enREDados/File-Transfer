import socket
import sys

import lib.constants

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

    def acceptConnection(self):
        mensaje = b"Buenas tardes, acepto tu conexion. Aca te mando mi addr"

        self.skt.sendto(mensaje, self.peerAddr)

    def connect(self):
        # ATTENTION: ¿La forma de conectarse es la misma entre stop and
        # wait y selective repeat?
        # ATTENTION: el "b" antes del string indica que son bytes
        mensaje = b"Hola buenas tardes me quiero conectar"

        self.skt.sendto(mensaje, self.peerAddr)

        # Aca, el server me responde. ¿La data es importante? 
        # Lo importante, es el addres. Esta tiene el puerto con el que
        # voy a hablar
        _, addr = self.skt.recvfrom(1024) # buffer size is 1024 bytes

        # Actualizo el peer addres, poniendo ahora el puerto nuevo
        self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], addr[lib.constants.PUERTOTUPLA])


    def sendall(self, mensaje):
        if self.tipo == "SW":
            self._sendall_stop_and_wait(mensaje)
        else:
            self._sendall_selective()
        return

    def receive_all(self, ):
        if self.tipo == "SW":
            return self._receive_stop_and_wait()
        else:
            return self._receive_selective()

    def shutdown(self, ):
        sys.exit("NO IMPLEMENTADO")

    def _sendall_stop_and_wait(self, mensaje):
        # WARNING: Esto NO ES ASI DE CORTO PARA NADA.
        # Solo para el test inicial
        self.skt.sendto(mensaje, self.peerAddr)
        pass
    def _sendall_selective(self,):
        sys.exit("NO IMPLEMENTADO")
        pass

    def _receive_stop_and_wait(self,):
        # Esto me va a devolver un addr y data.
        # addr yo "en teoria" ya lo conozco
        # data es lo importante
        data, _ = self.skt.recvfrom(1024) # buffer size is 1024 bytes

        return data

    def _receive_selective(self,):
        sys.exit("NO IMPLEMENTADO")
