import socket
import sys
import math
import time
import struct

import lib.constants

# ATTENTION: Ver comentario "STRUCTS" a pie de pagina
def intAUint32(numero:int) -> bytes:
    numeroEnUint = struct.pack(lib.constants.FORMATORED, numero)

    return numeroEnUint

def uint32Aint(bytesATransformar:bytes) -> int:
    intFinal = struct.unpack(lib.constants.FORMATORED, bytesATransformar)[0]

    return intFinal


# Esto mas que una clase es un struct. Lo hago aparte para que quede
# mas legible
class Paquete:

    # ATTENTION: Ver comentario "STRUCTS" a pie de pagina

    def __init__(self, sequence_number, datos: bytes):
        sequenceNumberBin = intAUint32(sequence_number)

        # datos.insert(0, sequenceNumberBin)
        self.misBytes = bytearray(sequenceNumberBin)
        self.misBytes.extend(datos)

class SocketRDT:
    def __init__(self, tipo, peerAddr, myIP, myPort=0):
        # Este socket representa el socket que yo voy a usar de OUTPUT.
        # Si a mi me quieren hablar. Yo tengo que bindear este socket
        # Si yo quiero hablar con alguien, uso la direccion para hablar
        self.skt = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        
        # Cuando bind tiene un 0 de segundo argumento nos da un puerto
        # nuevo cada vez. Fuente: https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
        # ATTENTION: Necesitamos bindearlo siempre porque tanto cliente
        # como servidor van a enviar y recibir cosas.
        self.skt.bind((myIP, myPort))

        # ATTENTION: No se si hace falta guardar "mi propio address"
        # Lo pongo por si lo llegamos a necesitar
        myPort = self.skt.getsockname()[1]
        self.myAddress = (myIP, myPort)

        self.peerAddr = peerAddr

        self.tipo = tipo

    def acceptConnection(self,):
        _, addr = self.skt.recvfrom(27) # buffer size is 1024 bytes

        return addr
        

    def syncAck(self):
        # Este mensaje podria ser mas corto o no estar directamente
        # Solo necesitamos mandarle esto para que reciba la direccion
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
        _, addr = self.skt.recvfrom(37) # buffer size is 1024 bytes

        # Actualizo el peer addres, poniendo ahora el puerto nuevo
        self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], addr[lib.constants.PUERTOTUPLA])


    def sendall(self, mensaje):
        mensajeEnBytes = mensaje.encode('utf-8')
        print(type(mensajeEnBytes))
        if self.tipo == "SW":
            self._sendall_stop_and_wait(mensajeEnBytes)
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


        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAQUETE
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)

        cantPaquetesUint32 = intAUint32(cantPaquetesAenviar)

        self.skt.sendto(cantPaquetesUint32, self.peerAddr)

        self.skt.settimeout(lib.constants.TIMEOUT);

        test = True
        numPaquete = 0
        while numPaquete < cantPaquetesAenviar:
            try:
                numPaqueteRecibo, _ = self.skt.recvfrom(5)
                numPaqueteRecibo = uint32Aint(numPaqueteRecibo)
                
                if numPaqueteRecibo != numPaquete:
                    # Yo le queria enviar un numero distinto; pero
                    # me dijo que estaba esperando un numero distinto
                    # en ese caso, tengo que enviarle lo que el espera
                    # esto deberia ser SIEMPRE? el numero anterior
                    # por como funciona el stop and wait
                    numPaquete = numPaqueteRecibo
                    raise IndexError

                # Cada paquete es: primeros 4 bytes para el secuence numbers
                # siguientes es data
                indiceInicial = numPaquete*lib.constants.TAMANOPAQUETE
                indiceFinal = (numPaquete + 1) *lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1 
                print(f"Numero paquete: {numPaquete}")

                payloadActual = mensaje[indiceInicial:indiceFinal]
                paquete = Paquete(numPaquete, payloadActual)

                # WARNING: Este codigo existe solo para dropear un paquete
                # articifialmente. Lo mismo la variable test
                if not(numPaquete == 2 and test == True):
                    self.skt.sendto(paquete.misBytes, self.peerAddr)
                else:
                    test = False
                    print("Pierdo un paquete a proposito")


                numPaquete += 1
            except TimeoutError:
                # Volver a ejecutar
                print("TIMEOUT")
                pass

            except IndexError:
                # Volver a ejecutar
                print("El otro perdio")
                pass

        self.skt.settimeout(None)


        sys.exit("\033[91mDE ACA EN ADELANTE, NO ESTA IMPLEMENTADO\033[0m")





        pass
    def _sendall_selective(self,):
        sys.exit("NO IMPLEMENTADO")
        pass

    def _receive_stop_and_wait(self,):
        # Esto me va a devolver un addr y data.
        # addr yo "en teoria" ya lo conozco
        # data es lo importante
        cantPaquetes, _ = self.skt.recvfrom(1024)
        cantPaquetes = uint32Aint(cantPaquetes)


        self.skt.settimeout(lib.constants.TIMEOUT);

        mensajeFinal = bytearray()
         
        test = True

        seqNum = 0
        while seqNum < cantPaquetes:
            try:
                # ATTENTION: Puede parecer extrano que el reciever le
                # mande el sequence number primero al sender.
                # Es medio raro.
                # Esta fue la mejor solucion que se me ocurrio al
                # problema de "Que pasa si EL SENDER" tiene timeout
                numPaqueteActualUint = intAUint32(seqNum)
                self.skt.sendto(numPaqueteActualUint, self.peerAddr)

                # WARNING: Este codigo existe solo para dropear un paquete
                # articifialmente. Lo mismo la variable test
                if seqNum == 3 and test == True:
                    print("Pierdo paquete")
                    test = False
                    continue

                data, _ = self.skt.recvfrom(1024) # buffer size is 1024 bytes

                seqNum = uint32Aint(data[0:lib.constants.TAMANOHEADER])
                seqNum += 1

                message = data[lib.constants.TAMANOHEADER + 1:]

                mensajeFinal.extend(message)
                print(seqNum)
                print(message)


                # numPaquete += 1
            except TimeoutError:
                # Volver a ejecutar
                print("TIMEOUT")
                pass

        # Lo ponemos de vuelta en modo bloqueante:
        # Fuente: https://docs.python.org/3/library/socket.html#socket.socket.settimeout
        self.skt.settimeout(None)

        sys.exit("\033[91mDE ACA EN ADELANTE, NO ESTA IMPLEMENTADO\033[0m")
        return 

    def _receive_selective(self,):
        sys.exit("NO IMPLEMENTADO")


# COMENTARIOS

## STRUCTS
# La "I" quiere decir que el sequence number va a tener
# formato como un uint 32_t.
# La "!" quiere decir que lo ponga en modo network
# Fuentes:
# https://docs.python.org/3/library/struct.html
# https://docs.python.org/3/library/struct.html#struct-format-strings
