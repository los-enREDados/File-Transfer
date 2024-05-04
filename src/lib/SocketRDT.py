import socket
import sys
import math
import datetime
import struct
from enum import Enum

class Tipo(Enum):
    UPLOAD = 1
    DOWNLOAD = 2

import lib.constants

# ATTENTION: Ver comentario "STRUCTS" a pie de pagina
def intAUint32(numero:int) -> bytes:
    numeroEnUint = struct.pack(lib.constants.FORMATORED, numero)

    return numeroEnUint

def uint32Aint(bytesATransformar:bytes) -> int:
    intFinal = struct.unpack(lib.constants.FORMATORED, bytesATransformar)[0]

    return intFinal

def strABytes(string: str) -> bytes:
    strEnBytes = string.encode('utf-8')
    return strEnBytes

def bytesAstr(bytesOrigen: bytes) -> str:
    stringObtenido = bytesOrigen.decode('utf-8')

    return stringObtenido


class CeldaSR:
    def __init__(self, tiempoDeEnvio=None, ackeado=False):
        self.tiempoDeEnvio = tiempoDeEnvio
        self.ackeado = ackeado
    def __repr__(self):
        return f"Tiempo de envio: {self.tiempoDeEnvio},Ackeado: {self.ackeado}"
# Copilot please reboot my computer
# Go go gadget

# Esto mas que una clase es un struct. Lo hago aparte para que quede
# mas legible
class Paquete:

    # ATTENTION: Ver comentario "STRUCTS" a pie de pagina
    '''
        |-------------------|
        | Seq number | Fin  |
        |------------+------|
        |                   |
        |     Data   :D     |
        |-------------------|
    '''
    #                     4 bytes      1 byte
    def __init__(self, sequence_number, fin, datos: bytes):
        sequenceNumberBin = intAUint32(sequence_number)
        
        self.seqNum = sequenceNumberBin
        self.fin = fin
        self.payload = datos

        self.misBytes = bytearray(sequenceNumberBin)
        self.misBytes.extend(fin.to_bytes(1, 'big'))
        self.misBytes.extend(datos)
    
    def getPayload(self):        
        return self.payload

    def getSequenceNumber(self):
        seqNumLocal = uint32Aint(self.seqNum)
        return seqNumLocal

    @staticmethod 
    def Paquete_from_bytes(bytes_paquete: bytes):    
        seqNum = uint32Aint(bytes_paquete[0:lib.constants.TAMANONUMERORED])
        fin = bytes_paquete[lib.constants.TAMANONUMERORED]
        payload = bytes_paquete[lib.constants.TAMANOHEADER:]
        return Paquete(seqNum, fin, payload)



class SocketRDT:
    #                                        myPort=0 significa que me
    #                                        va a dar un puerto random
    #                                        cada vez. El listener/Server
    #                                        necesita especificarlo; al
    #                                        cliente no le importa cual
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
        print(self.skt.getsockname())

        # ATTENTION: No se si hace falta guardar "mi propio address"
        # Lo pongo por si lo llegamos a necesitar
        myPort = self.skt.getsockname()[1]
        self.myAddress = (myIP, myPort)

        self.peerAddr = peerAddr

        self.tipo = tipo

    def acceptConnection(self,):
        mensajeConeccion = b""

        # Voy a pedir conecciones hasta que alguien me mande el SYN
        while mensajeConeccion != lib.constants.MENSAJECONECCION:
            print(f"Server esperando conexiones en {self.myAddress}")
            mensajeConeccion, addr = self.skt.recvfrom(len(lib.constants.MENSAJECONECCION))
            print(f"Recibi {mensajeConeccion} mensaje de {addr}")
        return addr
        

    def syncAck(self, puertoNuevo: int, socketRDT):
        # Este mensaje podria ser mas corto o no estar directamente
        # Solo necesitamos mandarle esto para que reciba la direccion
        # mensaje = lib.constants.MENSAJEACEPTARCONECCION
        mensaje = intAUint32(puertoNuevo)
        print(type(mensaje))

        
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)
        synAckAck = b""
        maxTimeouts = 4
        timeouts = 0 
        while synAckAck != lib.constants.MENSAJEACK:
            try: 
                # Si me llego este mensaje significa que NO LE LLEGO. 
                print("Viendo si recibo algo en synACK")
                self.skt.sendto(mensaje, socketRDT.peerAddr)
                synAckAck, addr = self.skt.recvfrom(len(lib.constants.MENSAJECONECCION), socket.MSG_PEEK)

                if synAckAck == lib.constants.MENSAJEACEPTARCONECCION:
                    synAckAck, addr = self.skt.recvfrom(len(lib.constants.MENSAJECONECCION))

            except TimeoutError:
                print("syncACK(): Timeout")
                timeouts += 1
                if timeouts >= maxTimeouts:
                    print("syncACK(): Asumo que llego")
                    break
                return False
        print("syncACK() Fin")





    def connect(self):
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)
        nuevoPuerto = b""
        addr = 0

        while nuevoPuerto == b"":
            try: 
                print("connect() enviando SYN")
                self.skt.sendto(lib.constants.MENSAJECONECCION, self.peerAddr)
                nuevoPuerto, addr = self.skt.recvfrom(lib.constants.TAMANONUMERORED) 
                if addr[0] != self.peerAddr[0]:
                    print("Contesto otro server")
                    raise ValueError("Se conecto a otro servidor")

            except TimeoutError:
                # Volver a ejecutar
                print("TIMEOUT")
                pass
          
        nuevoPuerto = uint32Aint(nuevoPuerto)
        self.skt.settimeout(None)
        self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], nuevoPuerto)


        return

    def sendall(self, mensaje:bytes):
        if self.tipo == "SW":
            self._sendall_stop_and_wait(mensaje)
        else:
            self._sendall_selective(mensaje)
        return

    def receive_all(self, ):
        if self.tipo == "SW":
            return self._receive_stop_and_wait()
        else:
            return self._receive_selective()

    def shutdown(self, ):
        sys.exit("NO IMPLEMENTADO")

    def _recieve(self, tam) -> bytes:
        mensaje, addr = self.skt.recvfrom(tam)
        if addr != self.peerAddr:
            # Aca no levantaria error, simplemente dropeariamos
            raise ValueError("Recibi mensaje de una IP que no es mi peer.")
        
        return mensaje

    def _pkt_sent_ok(self, ack_pkt: bytes, seqNum: int):
        # Aclaracion: El ACK es directamente el numero de 
        # paquete recibido por el otro
        seqNumRecibido = uint32Aint(ack_pkt)

        return seqNumRecibido == seqNum

    def _sendall_stop_and_wait(self, mensaje: bytes):
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)

        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAQUETE
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)

        print(f"cantPaquetesAenviar: {cantPaquetesAenviar}")

        seqNum = 0
        while seqNum <= cantPaquetesAenviar:
           
            try: 

                indiceInicial = seqNum * lib.constants.TAMANOPAQUETE
                indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1

                payloadActual = mensaje[indiceInicial:indiceFinal]

                
                if seqNum == cantPaquetesAenviar:
                    paquete = Paquete(seqNum, lib.constants.FIN, payloadActual)
                else:
                    paquete = Paquete(seqNum, lib.constants.NOFIN, payloadActual)

                print(f"Enviando paquete a {self.peerAddr}")
                print(f"seqNum: {seqNum}")
                self.skt.sendto(paquete.misBytes, self.peerAddr)

                # Recibimos el ACK de que el paquete llego
                # Aca puede quedar bloqueado hasta que salte el timeout
                ack_pkt = self._recieve(lib.constants.TAMANONUMERORED)
                
                if self._pkt_sent_ok(ack_pkt, seqNum):
                    seqNum += 1

                else:
                    continue
                    seqNum = 0
                
            except TimeoutError:
                # Volver a ejecutar
                print("TIMEOUT")
                pass
            
        self.skt.settimeout(None)
    
        return
    

    def _receive_stop_and_wait(self,):
        mensajeFinal = bytearray()

        es_fin = False
        ultimoSeqNumACK = -1
        while not es_fin:

            bytes_paquete = self._recieve(lib.constants.TAMANOPAQUETE + lib.constants.TAMANOHEADER)
       
            paquete = Paquete.Paquete_from_bytes(bytes_paquete)

            seqNumRecibido = paquete.getSequenceNumber() #5
            
            # Agrego mi paquete al mensaje final
            if ultimoSeqNumACK != seqNumRecibido:
                payload = paquete.getPayload()
                mensajeFinal.extend(payload)

            ultimoSeqNumACK = seqNumRecibido


            es_fin = paquete.fin
            
            # Envio ACK
            seqNumAEnviar = paquete.getSequenceNumber()
            self.skt.sendto(intAUint32(seqNumAEnviar), self.peerAddr)
        
        return mensajeFinal

    def _chequear_timeouts(self, lista_de_timeouts, tiempo_ahora, ventana):
        lista_de_timeouts_actualizada = lista_de_timeouts

        seq_number_perdido = -1
        for i in range(ventana[0], ventana[1] + 1):
            celda = lista_de_timeouts_actualizada[i]
            seq_number = i
            tiempo_de_envio = celda.tiempoDeEnvio
            # Si todavia no tiene envio, no hago nada
            if tiempo_de_envio == None:
                continue

            # Si ya fue ACK, no lo quiero volver a enviar; incluso con
            # timeout.
            # NOTE: ESTO EN TEORIA (y segun las corridass que hicimos)
            # no pasa
            fue_ack = celda.ackeado
            if fue_ack == True:
                print("Ya fue ACKEADO")
                continue

            segundos_sin_ack = (tiempo_ahora - tiempo_de_envio).total_seconds()
            # print(f"SEGUNDOS SIN ACK: {segundos_sin_ack}")

            # Apenas encuentro uno, lo quiero reenviar
            if segundos_sin_ack > lib.constants.TIEMOUTPORPAQUETESR:
                seq_number_perdido = i
                break

        # No lo saco por miedo a sacar algo en el medio de un for
        if seq_number_perdido != -1:
            # NOTE: Lo saco de la lista de timeouts porque "ya no aplica ese timeout".
            # Cuando envie de nuevo el paquete perdido, voy a volver a actualizar la lista
            lista_de_timeouts_actualizada[seq_number_perdido].tiempoDeEnvio = None
            
        return seq_number_perdido, lista_de_timeouts_actualizada

    def _obtener_nuevo_comienzo_ventana(self, listaDeTimeouts, window):
        for i in range(window[0], window[1]+1):
            boolActual = listaDeTimeouts[i].ackeado
            if boolActual == False:
                print(f"Recibi el ack de secuencia: {i}")
                return i

        return window[1] + 1

    def _enviar_paquete_SR(self, mensaje: bytes, seqNum: int, list_de_timeouts, cantPaquetesAenviar:int, ventana, cantidadACK):

        celdaAEnviar = list_de_timeouts[seqNum]

        # Esto significa que el sequence number que corresponde al paquete
        # ya fue enviado. Y esto epserando su ACK.
        if celdaAEnviar.tiempoDeEnvio != None:
            # print("ESTE PAQUETE FUE ENVIADO")
            return list_de_timeouts, False

        elif celdaAEnviar.ackeado == True:
            # print("ESTE PAQUETE YA FUE ACKEADO")
            return list_de_timeouts, False

        # NOTE: Theo ama esto <3
        if seqNum < ventana[0] or seqNum > ventana[1]:
            print("JAMON")
            sys.exit("FUERA DE LA VENTANA >:D")


        # NOTE: Si llegue hasta significa que hay espacio en la ventana

        indiceInicial = seqNum * lib.constants.TAMANOPAQUETE
        indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1
        payloadActual = mensaje[indiceInicial:indiceFinal]

        print(f"MANDO EL PAQUETE CON SEQ {seqNum}")

        paquete = Paquete(seqNum, lib.constants.NOFIN, payloadActual)

        self.skt.sendto(paquete.misBytes, self.peerAddr)

        lista_de_timeoutes_actualizada = list_de_timeouts



        tiempoActual =  datetime.datetime.now()
        lista_de_timeoutes_actualizada[seqNum] = CeldaSR(tiempoActual, False)

        pudeEnviar = True
        return lista_de_timeoutes_actualizada, pudeEnviar


    def _is_ventana_full(self, ventana):
        return
    
    def _actualiza_acks_sr(self, listaDeTimeouts, seqNumRecibido, cantidadDeACKS):
        lista_de_timeoutes_actualizada = listaDeTimeouts

        if lista_de_timeoutes_actualizada[seqNumRecibido].ackeado == False:
            cantidadDeACKS += 1
        lista_de_timeoutes_actualizada[seqNumRecibido].tiempoDeEnvio = None
        lista_de_timeoutes_actualizada[seqNumRecibido].ackeado = True 
        
        return lista_de_timeoutes_actualizada, cantidadDeACKS

    def _recibir_paquetes_sender_SR(self, listaDeTimeouts, cantidadDePaquetesACKs, ventana, cantPaquetesAenviar, tamanoVentana, envieTodo):
        minSeqRecibido = None
        try:
            while True:
                ack_pkt = self._recieve(lib.constants.TAMANONUMERORED)


                seqNumRecibido = uint32Aint(ack_pkt)

                listaDeTimeouts, cantidadDePaquetesACKs = self._actualiza_acks_sr(listaDeTimeouts, seqNumRecibido, cantidadDePaquetesACKs)
                if minSeqRecibido == None:
                    minSeqRecibido = seqNumRecibido
                else:
                    if seqNumRecibido < minSeqRecibido:
                        minSeqRecibido = seqNumRecibido

                print(f"CANTIDAD ACKS {cantidadDePaquetesACKs}")

        except BlockingIOError:
            print("BLOCKING ERROR")
            if minSeqRecibido == None:
                return listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo
            elif minSeqRecibido == ventana[0]:
                print("EXPANDO VENTANA")
                nuevoComienzoVentana = self._obtener_nuevo_comienzo_ventana(listaDeTimeouts, ventana)

                if nuevoComienzoVentana >= cantPaquetesAenviar:
                    envieTodo = True
                nuevoFin = min(cantPaquetesAenviar - 1, nuevoComienzoVentana + tamanoVentana)

                ventana = [nuevoComienzoVentana, nuevoFin]
        return listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo

    def _sendall_selective(self, mensaje: bytes):

        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAQUETE
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)


        # ATTENTION: Chequear si realmente es // 2
        tamanoVentana = math.ceil(cantPaquetesAenviar / 2)

        # ATTENTION: La ventana es una lista de dos valores. Siendo el
        # inicio inclusive y el fin inclusive
        ventana = [0, tamanoVentana - 1]

        # NOTE: Lista de timeouts es una lista de tuplas que representa
        # (Sequence number, tiempo de envio [clase datetime de Python])
        # La inicializo "con valores default"
        # listadeTimeous = [(tiempoDeEnvio, ackeado), ...]
        listaDeTimeouts = [CeldaSR()] * cantPaquetesAenviar

        seqNumAEnviar = 0
        seqNumActual = 0 
        cantidadDePaquetesACKs = 0
        print("HOLA")

        self.skt.setblocking(False)

        envieTodo = False
        while envieTodo == False:
            huboTimeout = False
            print(f"VALOR VENTANA: {ventana}")
            tiempoActual =  datetime.datetime.now()

            seqNumPerdido, listaDeTimeouts = self._chequear_timeouts(listaDeTimeouts, tiempoActual, ventana)

            if seqNumPerdido != -1:
                print("HUBO UN TIMEOUT LOCAL DE LOS NUESTROS")
                seqNumAEnviar = seqNumPerdido
                huboTimeout = True

            else:
                seqNumAEnviar = seqNumActual
                if seqNumAEnviar < ventana[1]:
                    seqNumActual += 1


            listaDeTimeouts, pudeEnviar = self._enviar_paquete_SR(mensaje, seqNumAEnviar, listaDeTimeouts, cantPaquetesAenviar, ventana, cantidadDePaquetesACKs)

            # NOTE: No va a poder enviar cuando la ventana este llena
            if pudeEnviar == True and huboTimeout == False:
                continue

            print("ESCUCHO")
            listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo = self._recibir_paquetes_sender_SR(listaDeTimeouts, cantidadDePaquetesACKs, ventana, cantPaquetesAenviar, tamanoVentana, envieTodo)

        self.skt.setblocking(True)

        self.skt.settimeout(lib.constants.TIMEOUTSENDERSR)

        maxTimeouts = 4
        timeoutCount = 0
        llegoFin = False
        while llegoFin == False:
            try:
                paquete = Paquete(seqNumActual + 1, lib.constants.FIN, b"")

                self.skt.sendto(paquete.misBytes, self.peerAddr)

                ack_pkt = self._recieve(lib.constants.TAMANONUMERORED)

                seqNumRecibido = uint32Aint(ack_pkt)

                if seqNumRecibido == seqNumActual + 1:
                    break
            except TimeoutError:
                timeoutCount += 1
                if timeoutCount > maxTimeouts:
                    break
                print("TIMEOUT")
                pass

        self.skt.settimeout(None)  

        print("TERMINE DE MANDAR")


    def _receive_selective(self,):
        # NOTE: Uso un diccionario como mejor acercamiento a un buffer
        # Las entradas del diccionario son:
        # "sequence number" : "payload"
        mensajeFinal = {}
        es_fin = False
        cant_recibidos = 0
        seq_num_de_fin = None

        # [0, 1, 2, 3, 4]
        # [0, 1, 2, 3, 4]
        # cant_recibios = 5

        self.skt.settimeout(100)
        try:
            while True:
                print(f"{cant_recibidos}")
                if seq_num_de_fin != None and cant_recibidos == seq_num_de_fin+1:
                    print("BREAK")
                    pass
                    break

                bytes_paquete = self._recieve(lib.constants.TAMANOPAQUETE + lib.constants.TAMANOHEADER)

                paquete = Paquete.Paquete_from_bytes(bytes_paquete)

                seqNumRecibido = paquete.getSequenceNumber() #5

                print(f"|  Recibi seqNum: {seqNumRecibido}")

                self.skt.sendto(intAUint32(seqNumRecibido), self.peerAddr)

                payload = paquete.getPayload()

                es_fin = paquete.fin
                if es_fin == True and seqNumRecibido not in mensajeFinal:
                    print("LLEGO EL FIN")
                    seq_num_de_fin = seqNumRecibido

                if seqNumRecibido not in mensajeFinal:
                    mensajeFinal[seqNumRecibido] = payload
                    cant_recibidos += 1

        except TimeoutError:
            print("WARNING: Timeout, asumo que termino")



        mensaje = bytearray()
        for i in range(cant_recibidos):
            mensaje.extend( mensajeFinal[i])
        
        return mensaje 
        sys.exit("NO IMPLEMENTADO")


# COMENTARIOS

## STRUCTS
# La "I" quiere decir que el sequence number va a tener
# formato como un uint 32_t.
# La "!" quiere decir que lo ponga en modo network
# Fuentes:
# https://docs.python.org/3/library/struct.html
# https://docs.python.org/3/library/struct.html#struct-format-strings
        '''
        

        | 0     | 0         |
        |                   |
        |     Data          |
        |                   |

        | 1     | 0         |
        |                   |
        |     Data          |
        |                   |

        | 2     | 1         |
        |                   |
        |     Data          |
        |                   |
        
        '''
