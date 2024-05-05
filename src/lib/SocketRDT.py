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
        +---------------------+---------------------+-------------------+
        | Sequence Number 4b | Connect 1B | Tipo 1B | Fin 1B | Error 1B |
        +---------------------+---------------------+-------------------+
        |                                                               |
        |                            Data 500B                          |
        |                                                               |
        +---------------------+---------------------+-------------------+
    
    '''
    #                       4bytes            1byte     1byte     1bytes    1bytes       500bytes
    def __init__(self, sequence_number:int, connect:int, tipo:int, fin:int, error:int, datos: bytes):
        sequenceNumberBin = intAUint32(sequence_number)
        
        self.connect = connect
        self.tipo = tipo
        self.seqNum = sequenceNumberBin
        self.fin = fin
        self.error = error
        self.payload = datos

        self.misBytes = bytearray(sequenceNumberBin)
        self.misBytes.extend(connect.to_bytes(1, 'big'))
        self.misBytes.extend(tipo.to_bytes(1, 'big'))
        self.misBytes.extend(fin.to_bytes(1, 'big'))
        self.misBytes.extend(error.to_bytes(1, 'big'))
        self.misBytes.extend(datos)
    
    def getPayload(self):        
        return self.payload

    def getSequenceNumber(self):
        seqNumLocal = uint32Aint(self.seqNum)
        return seqNumLocal

    @staticmethod 
    def Paquete_from_bytes(bytes_paquete: bytes):
        seqNum  = uint32Aint(bytes_paquete[0:lib.constants.TAMANONUMERORED])
        connect = bytes_paquete[lib.constants.TAMANONUMERORED]
        tipo = bytes_paquete[lib.constants.TAMANONUMERORED + 1]
        fin = bytes_paquete[lib.constants.TAMANONUMERORED + 2]
        error = bytes_paquete[lib.constants.TAMANONUMERORED + 3]
        payload = bytes_paquete[lib.constants.TAMANOHEADER:]

        return Paquete(seqNum, connect, tipo, fin, error, payload)



class SocketRDT:
    #                                        myPort=0 significa que me
    #                                        va a dar un puerto random
    #                                        cada vez. El listener/Server
    #                                        necesita especificarlo; al
    #                                        cliente no le importa cual
    def __init__(self, protocolo, tipo , peerAddr, myIP, myPort=0):
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

        self.protocolo = protocolo
        self.tipo = tipo
        self.peerAddr = peerAddr
        

    def acceptConnection(self,):
        mensajeConeccion = b""

        paquete = None

        # Voy a pedir conecciones hasta que alguien me mande el SYN
        while mensajeConeccion != lib.constants.CONNECT:
            print(f"Server esperando conexiones en {self.myAddress}")
            paquete_recibido, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE)
            paquete = Paquete.Paquete_from_bytes(paquete_recibido)
            mensajeConeccion = paquete.connect
            print(f"Recibi {mensajeConeccion} mensaje de {addr}")
            
        return paquete, addr
        

    def syncAck(self, puertoNuevo: int, socketRDT, paqueteRecibido):
        # Este mensaje podria ser mas corto o no estar directamente
        # Solo necesitamos mandarle esto para que reciba la direccion
        # mensaje = lib.constants.MENSAJEACEPTARCONECCION
        datos = intAUint32(puertoNuevo)

        tipoConexion = paqueteRecibido.tipo
        paquete = Paquete(0, lib.constants.CONNECT, tipoConexion, 0, 0, datos)
        # print(type(mensaje))

        
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)
        synAckAck = b""
        maxTimeouts = 4
        timeouts = 0 
        while synAckAck != lib.constants.MENSAJEACK:
            try: 
                # Si me llego este mensaje significa que NO LE LLEGO. 
                print("Viendo si recibo algo en synACK")
                self.skt.sendto(paquete.misBytes, socketRDT.peerAddr)
                paquete_bytes, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE, socket.MSG_PEEK)
                paquete = Paquete.Paquete_from_bytes(paquete_bytes)

                if addr != socketRDT.peerAddr:
                    print("Contesto otro server")
                  
                if paquete.connect == lib.constants.CONNECT :
                    synAckAck, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE)
                    return True

            except TimeoutError:
                print("syncACK(): Timeout")
                timeouts += 1
                if timeouts >= maxTimeouts:
                    print("syncACK(): Asumo que llego")
                    break
                # return False
            
            
        print("syncACK() Fin")

    def connect(self, tipo, nombre_archivo):
        msg_bytes = strABytes(nombre_archivo)
        paquete = Paquete(0, lib.constants.CONNECT, tipo, lib.constants.NOFIN, 0, msg_bytes)
        
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)
        nuevoPuerto = b""
        addr = 0

        while True:
            try: 
                print("connect() enviando SYN")
                self.skt.sendto(paquete.misBytes, self.peerAddr)
                paqueteRecibido, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE) 
                if addr[0] != self.peerAddr[0]:
                    print("Contesto otro server")
                    raise ValueError("Se conecto a otro servidor")

                break
            except TimeoutError:
                # Volver a ejecutar
                print("TIMEOUT")
                pass
        
        paqueteRecibido = Paquete.Paquete_from_bytes(paqueteRecibido)
        nuevoPuerto = uint32Aint(paqueteRecibido.getPayload())
        self.skt.sendto(paquete.misBytes, self.peerAddr)

        self.skt.settimeout(None)
        print (f"Nuevo puerto recibido en connect: {nuevoPuerto}")
        self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], nuevoPuerto)


        return

    def sendall(self, mensaje:bytes):
        if self.protocolo == "SW":
            self._sendall_stop_and_wait(mensaje)
        else:
            self._sendall_selective(mensaje)
        return

    def receive_all(self, ):
        if self.protocolo == "SW":
            return self._receive_stop_and_wait()
        else:
            return self._receive_selective()

    def shutdown(self, ):
        sys.exit("NO IMPLEMENTADO")

    def _recieve(self, tam=lib.constants.TAMANOPAQUETE + 16) -> Paquete:
        paquete_bytes, addr = self.skt.recvfrom(tam)
        
        if addr != self.peerAddr:
            print("Recibi un paquete de otro lado")
            return None
        paquete = Paquete.Paquete_from_bytes(paquete_bytes)
        return paquete

    def _pkt_sent_ok(self, ack_pkt: int, seqNum: int):
        # Aclaracion: El ACK es directamente el numero de 
        # paquete recibido por el otro
        seqNumRecibido = ack_pkt

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
                    paquete = Paquete(seqNum, lib.constants.NOCONNECT, self.tipo, lib.constants.FIN, 0, payloadActual)
                else:
                    paquete = Paquete(seqNum, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, 0, payloadActual)

                print(f"Enviando paquete a {self.peerAddr}")
                print(f"seqNum: {seqNum}")
                self.skt.sendto(paquete.misBytes, self.peerAddr)

                # Recibimos el ACK de que el paquete llego
                # Aca puede quedar bloqueado hasta que salte el timeout
                paquete_ack = self._recieve()

                ack_pkt = paquete.getSequenceNumber()
                
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

            paquete = self._recieve()
       
            seqNumRecibido = paquete.getSequenceNumber() #5
            
            # Agrego mi paquete al mensaje final
            if seqNumRecibido == ultimoSeqNumACK + 1:
                print(f"Me llego bien el seqNum: {seqNumRecibido}")
                payload = paquete.getPayload()
                mensajeFinal.extend(payload)

                ultimoSeqNumACK = seqNumRecibido


            es_fin = paquete.fin
            
            # Envio ACK
            seqNumAEnviar = paquete.getSequenceNumber()
            paqueteAck = Paquete(seqNumAEnviar, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, 0, b"")

            self.skt.sendto(paqueteAck.misBytes, self.peerAddr)
        
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

        if seqNum < ventana[0] or seqNum > ventana[1]:
            sys.exit("FUERA DE LA VENTANA >:D")


        # NOTE: Si llegue hasta significa que hay espacio en la ventana

        indiceInicial = seqNum * lib.constants.TAMANOPAQUETE
        indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1
        payloadActual = mensaje[indiceInicial:indiceFinal]
        # print( f"mensaje inicial: {indiceInicial} mensaje final: {indiceFinal} payload: {payloadActual}")

        paquete = Paquete(seqNum, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, 0, payloadActual)

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
                ack_pkt = self._recieve()
                if not ack_pkt: continue #droppeamos paquete de otro lado

                seqNumRecibido = ack_pkt.getSequenceNumber()

                listaDeTimeouts, cantidadDePaquetesACKs = self._actualiza_acks_sr(listaDeTimeouts, seqNumRecibido, cantidadDePaquetesACKs)
                if minSeqRecibido == None:
                    minSeqRecibido = seqNumRecibido
                else:
                    if seqNumRecibido < minSeqRecibido:
                        minSeqRecibido = seqNumRecibido


        except BlockingIOError:
            if minSeqRecibido == None:
                return listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo
            elif minSeqRecibido == ventana[0]:
                nuevoComienzoVentana = self._obtener_nuevo_comienzo_ventana(listaDeTimeouts, ventana)

                if nuevoComienzoVentana >= cantPaquetesAenviar:
                    envieTodo = True
                nuevoFin = min(cantPaquetesAenviar - 1, nuevoComienzoVentana + tamanoVentana)

                ventana = [nuevoComienzoVentana, nuevoFin]
        return listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo
    

    def _sendall_selective(self, mensaje: bytes):

        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAQUETE
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)

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

        self.skt.setblocking(False)

        envieTodo = False
        while envieTodo == False:
            huboTimeout = False
            # print(f"VALOR VENTANA: {ventana}")
            tiempoActual =  datetime.datetime.now()

            seqNumPerdido, listaDeTimeouts = self._chequear_timeouts(listaDeTimeouts, tiempoActual, ventana)

            if seqNumPerdido != -1:
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

            listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo = self._recibir_paquetes_sender_SR(listaDeTimeouts, cantidadDePaquetesACKs, ventana, cantPaquetesAenviar, tamanoVentana, envieTodo)

            print_loading_bar(cantidadDePaquetesACKs / cantPaquetesAenviar)

        self.skt.setblocking(True)

        self.skt.settimeout(lib.constants.TIMEOUTSENDERSR)

        maxTimeouts = 4
        timeoutCount = 0
        llegoFin = False
        while llegoFin == False:
            try:
                paquete = Paquete(seqNumActual + 1, lib.constants.NOCONNECT, self.tipo, lib.constants.FIN, 0, b"")

                self.skt.sendto(paquete.misBytes, self.peerAddr)

                ack_pkt = self._recieve()
                if not ack_pkt:
                    continue

                seqNumRecibido = ack_pkt.getSequenceNumber()

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

        self.skt.settimeout(10)
        try:
            while True:
                if seq_num_de_fin != None and cant_recibidos == seq_num_de_fin+1:
                    break

                paquete = self._recieve()

                if (paquete.tipo != self.tipo or  paquete.connect != lib.constants.NOCONNECT or paquete.error != lib.constants.NOERROR):
                    print("ERROR: Recibi un paquete que no esperaba")
                    continue

                seqNumRecibido = paquete.getSequenceNumber()

                print(f"|  Recibi seqNum: {seqNumRecibido}")


                # paquete_ack = Paquete(seqNumRecibido, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, 0, b"")
                self.skt.sendto(paquete.misBytes, self.peerAddr)

                es_fin = paquete.fin
                if es_fin == True and seqNumRecibido not in mensajeFinal:
                    print("LLEGO EL FIN")
                    seq_num_de_fin = seqNumRecibido

                if seqNumRecibido not in mensajeFinal:
                    mensajeFinal[seqNumRecibido] = paquete.payload
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


def print_loading_bar(percentage, bar_length=20, fill_char='█', empty_char='-'):
  """
  Prints a progress bar to the console with a given percentage.

  Args:
      percentage (float): The percentage of completion (0.0 to 1.0).
      bar_length (int, optional): The length of the progress bar. Defaults to 20.
      fill_char (str, optional): The character to fill the completed portion. Defaults to '█'.
      empty_char (str, optional): The character to fill the remaining portion. Defaults to '-'.
  """
  filled_length = int(round(bar_length * percentage))
  filled_bar = fill_char * filled_length
  empty_bar = empty_char * (bar_length - filled_length)
  completion = f"{percentage:.2%}"

  print(f"[ {filled_bar}{empty_bar} ] {completion}", end="\r")

