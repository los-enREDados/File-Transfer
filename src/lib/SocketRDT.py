import socket
import sys
import math
import datetime
import struct
from enum import Enum

# class Tipo(Enum):
#     UPLOAD = 1
#     DOWNLOAD = 2

import lib.constants

class ConnectionTimedOutError(Exception):
    pass

class ConnectionAttemptTimedOutError(Exception):
    pass

class PackageError(Exception):
    pass

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

        # print(f"Bindiando en {myIP} y {myPort}")
        try:
            self.skt.bind((myIP, myPort))
        except OSError:
            raise OSError("No se pudo bindear el socket")

        # ATTENTION: No se si hace falta guardar "mi propio address"
        # Lo pongo por si lo llegamos a necesitar
        myPort = self.skt.getsockname()[1]
        self.myAddress = (myIP, myPort)

        self.protocolo = protocolo
        self.tipo = tipo
        self.peerAddr = peerAddr
        
        # 0 == no hubo error
        self.error = 0

    def acceptConnection(self):
        self.skt.settimeout(2)
        mensajeConeccion = b""

        paquete = None

        # Voy a pedir conecciones hasta que alguien me mande el SYN
        try: 
            paquete_recibido, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE)
            paquete = Paquete.Paquete_from_bytes(paquete_recibido)
            mensajeConeccion = paquete.connect
            print(f"Recibi {mensajeConeccion} mensaje de {addr}")


        except TimeoutError:
            raise ConnectionAttemptTimedOutError()
            
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
        maxTimeouts = 4
        timeouts = 0 
        while True:
            try: 
                # Si me llego este mensaje significa que NO LE LLEGO. 
                print("Viendo si recibo algo en synACK")
                self.skt.sendto(paquete.misBytes, socketRDT.peerAddr)
                paquete_bytes, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE)

                paquete_recibido= Paquete.Paquete_from_bytes(paquete_bytes)

                if addr != socketRDT.peerAddr: continue

                  
                if paquete_recibido.connect == lib.constants.CONNECT and paquete_recibido.fin == lib.constants.FIN:
                    _, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE)
                    print("syncACK(): confirmacion de conexion")
                    break

            except TimeoutError:
                timeouts += 1
                if timeouts >= maxTimeouts:
                    print("syncACK(): Asumo que llego")
                    break
            
            
        print("syncACK() Fin")

    def connect(self, tipo, nombre_archivo):
        msg_bytes = strABytes(nombre_archivo)
        paquete = Paquete(0, lib.constants.CONNECT, tipo, lib.constants.NOFIN, 0, msg_bytes)
        
        self.skt.settimeout(lib.constants.TIMEOUTCONNECT)
        nuevoPuerto = b""
        addr = 0

        timeouts = 0
        maxTimeouts = 100

        while True:
            try: 
                #print("connect() enviando SYN")
                self.skt.sendto(paquete.misBytes, self.peerAddr)
                
                paqueteRecibido, addr = self.skt.recvfrom(lib.constants.TAMANOPAQUETE) 
                if addr[0] != self.peerAddr[0]:
                    print("Contesto otro server")
                    raise ValueError("Se conecto a otro servidor")

                break

            except TimeoutError:
                # Volver a ejecutar
                timeouts += 1
                if (timeouts >= maxTimeouts):
                    raise ConnectionTimedOutError("CONNECTION TIMED OUT")
                print("TIMEOUT")
                pass
        
        paqueteRecibido = Paquete.Paquete_from_bytes(paqueteRecibido)
        #print(f'paquete recibido en syn: {paqueteRecibido.getPayload()} , {len(paqueteRecibido.getPayload())}')

        nuevoPuerto = uint32Aint(paqueteRecibido.getPayload())
        print (f"Nuevo puerto recibido en connect: {nuevoPuerto}")

        paquete_fin = Paquete(0, lib.constants.CONNECT, tipo, lib.constants.FIN, 0, b"")


        self.skt.sendto(paquete_fin.misBytes, self.peerAddr)

        self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], nuevoPuerto)

        self.skt.settimeout(None)

        return True

    def sendall(self, mensaje:bytes):
        # cant


        if mensaje == None:
            self.error = 1
            mensaje = b"ERROR"
        if self.protocolo == "SW":
            self._sendall_stop_and_wait(mensaje) #
        else:
            self._sendall_selective(mensaje) #
        return

    def receive_all(self, ):
        if self.protocolo == "SW":
            return self._receive_stop_and_wait()
        else:
            return self._receive_selective()

    def shutdown(self, ):
        self.skt.close()

    def _recieve(self, tam=lib.constants.TAMANOPAQUETE) -> Paquete:
        paquete_bytes, addr = self.skt.recvfrom(tam)
        
        paquete = Paquete.Paquete_from_bytes(paquete_bytes)

        if addr != self.peerAddr:
            return None

        return paquete

    def _pkt_sent_ok(self, ack_pkt: int, seqNum: int):
        # Aclaracion: El ACK es directamente el numero de 
        # paquete recibido por el otro
        seqNumRecibido = ack_pkt

        return seqNumRecibido == seqNum

    def _sendall_stop_and_wait(self, mensaje: bytes):
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)

        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAYLOAD
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)

        print(f"Cantidad de paquetes a enviar {cantPaquetesAenviar}")

        seqNum = 0
        while seqNum < cantPaquetesAenviar:
           
            try: 
                indiceInicial = seqNum * lib.constants.TAMANOPAYLOAD
                indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAYLOAD #ATTENTION: Ese es no inclusivo, va hasta indice final - 1

                payloadActual = mensaje[indiceInicial:indiceFinal]

                paquete = Paquete(seqNum, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, self.error, payloadActual)

                self.skt.sendto(paquete.misBytes, self.peerAddr)

                # Recibimos el ACK de que el paquete llego
                # Aca puede quedar bloqueado hasta que salte el timeout
                paquete_ack = self._recieve()
                if paquete_ack == None:
                    continue

                ack_pkt = paquete_ack.getSequenceNumber()
                
                if self._pkt_sent_ok(ack_pkt, seqNum):
                    seqNum += 1

                else:
                    continue   
            
                print_loading_bar(seqNum / cantPaquetesAenviar)
                
            except TimeoutError:
                continue

        self._send_fin(seqNum, cantPaquetesAenviar)    
        return
    
    def _receive_stop_and_wait(self):
        self.skt.settimeout(lib.constants.TIMEOUTRECEIVER)
        mensajeFinal = bytearray()

        es_fin = False
        ultimoSeqNumACK = -1
        while not es_fin:
            try :
                paquete = self._recieve()
                if paquete == None:
                    continue
        
                seqNumRecibido = paquete.getSequenceNumber() #5

                if paquete.error == 1:# and paquete.tipo == lib.constants.DOWNLOAD:
                    print(
                        "ERROR DE PAQUETE"
                    )
                    raise PackageError("")
                
                # Agrego mi paquete al mensaje final
                if seqNumRecibido == ultimoSeqNumACK + 1:
                    payload = paquete.getPayload()
                    mensajeFinal.extend(payload)

                    ultimoSeqNumACK = seqNumRecibido


                es_fin = paquete.fin
                if paquete.fin:
                    paquete_fin = Paquete(seqNumRecibido + 1, lib.constants.NOCONNECT, self.tipo, lib.constants.FIN, self.error, b"")
                    self.skt.sendto(paquete_fin.misBytes, self.peerAddr)
                
                # Envio ACK
                seqNumAEnviar = paquete.getSequenceNumber()
                paqueteAck = Paquete(seqNumAEnviar, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, self.error, b"")

                self.skt.sendto(paqueteAck.misBytes, self.peerAddr)

            except TimeoutError:
                raise ConnectionTimedOutError("CONNECTION TIMED OUT")
        
        self.skt.settimeout(None)
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

        indiceInicial = seqNum * lib.constants.TAMANOPAYLOAD
        indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAYLOAD #ATTENTION: Ese es no inclusivo, va hasta indice final - 1
        payloadActual = mensaje[indiceInicial:indiceFinal]
        # print( f"mensaje inicial: {indiceInicial} mensaje final: {indiceFinal} payload: {payloadActual}")

        paquete = Paquete(seqNum, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, self.error, payloadActual)

        self.skt.sendto(paquete.misBytes, self.peerAddr)

        lista_de_timeoutes_actualizada = list_de_timeouts


        tiempoActual =  datetime.datetime.now()
        lista_de_timeoutes_actualizada[seqNum] = CeldaSR(tiempoActual, False)

        pudeEnviar = True
        return lista_de_timeoutes_actualizada, pudeEnviar

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

        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAYLOAD
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)

        tamanoVentana = calculate_window_size(cantPaquetesAenviar)

        ventana = [0, tamanoVentana - 1]

        listaDeTimeouts = [CeldaSR()] * cantPaquetesAenviar

        seqNumAEnviar = 0
        seqNumActual = 0 
        cantidadDePaquetesACKs = 0
        timemouts_seguidos = 0

        self.skt.setblocking(False)

        print(f"Cantidad de paquetes a enviar {cantPaquetesAenviar}")
        envieTodo = False
        while envieTodo == False:
            huboTimeout = False
            tiempoActual =  datetime.datetime.now()

            seqNumPerdido, listaDeTimeouts = self._chequear_timeouts(listaDeTimeouts, tiempoActual, ventana)

            if seqNumPerdido != -1:
                timemouts_seguidos += 1
                print(f'largo de la ventana: {ventana[1] - ventana[0]}')
                print(f'timeouts seguidos: {timemouts_seguidos}')
                seqNumAEnviar = seqNumPerdido
                huboTimeout = True

            else:
                seqNumAEnviar = seqNumActual
                if seqNumAEnviar < ventana[1]:
                    timemouts_seguidos = 0
                    seqNumActual += 1

            if timemouts_seguidos > cantPaquetesAenviar :
                raise ConnectionTimedOutError("CONNECTION TIMED OUT")

            listaDeTimeouts, pudeEnviar = self._enviar_paquete_SR(mensaje, seqNumAEnviar, listaDeTimeouts, cantPaquetesAenviar, ventana, cantidadDePaquetesACKs)

            # NOTE: No va a poder enviar cuando la ventana este llena
            if pudeEnviar == True and huboTimeout == False:
                continue

            listaDeTimeouts, cantidadDePaquetesACKs, ventana, envieTodo = self._recibir_paquetes_sender_SR(listaDeTimeouts, cantidadDePaquetesACKs, ventana, cantPaquetesAenviar, tamanoVentana, envieTodo)

            print_loading_bar(cantidadDePaquetesACKs / cantPaquetesAenviar)


        self._send_fin(seqNumActual, cantPaquetesAenviar)

        print("TERMINE DE MANDAR")

    def _receive_selective(self,):
        # "sequence number" : "payload"
        mensajeFinal = {}

        cant_recibidos = 0
        seq_num_de_fin = None

        maxTimeouts = 4
        timeouts = 0
        self.skt.settimeout(lib.constants.TIMEOUTRECEIVER)
        while True:
            try:
                if seq_num_de_fin != None and cant_recibidos == seq_num_de_fin + 1:
                    print(f"Cantidad de recibidos: {cant_recibidos}")
                    break

                paquete = self._recieve()
                if paquete == None or paquete.tipo != self.tipo or lib.constants.NOCONNECT != paquete.connect or lib.constants.NOERROR != paquete.error:
                    continue #drop

                seqNumRecibido = paquete.getSequenceNumber()

                if paquete.error == 1:# and paquete.tipo == lib.constants.DOWNLOAD:
                    print(
                        "ERROR DE PAQUETE"
                    )
                    raise PackageError("")


                print(f"|  Recibi seqNum: {seqNumRecibido}")

                paquete_ack = Paquete(seqNumRecibido, lib.constants.NOCONNECT, self.tipo, lib.constants.NOFIN, 0, b"")
                self.skt.sendto(paquete_ack.misBytes, self.peerAddr)

                if paquete.fin == True and seqNumRecibido not in mensajeFinal:
                    seq_num_de_fin = seqNumRecibido

                if seqNumRecibido not in mensajeFinal:
                    mensajeFinal[seqNumRecibido] = paquete.payload
                    cant_recibidos += 1

            except TimeoutError:
                timeouts += 1
                if timeouts == maxTimeouts:
                    raise ConnectionTimedOutError("CONNECTION TIMED OUT")



        mensaje = bytearray()
        for i in range(cant_recibidos):
            mensaje.extend(mensajeFinal[i])
         
        return mensaje 

    def _send_fin(self, seqNumActual, cantPaquetesAenviar):
        self.skt.setblocking(True)

        self.skt.settimeout(lib.constants.TIMEOUTSENDERSR)

        maxTimeouts = 4
        timeoutCount = 0
        llegoFin = False
        while llegoFin == False:
            try:
                paquete = Paquete(cantPaquetesAenviar, lib.constants.NOCONNECT, self.tipo, lib.constants.FIN, 0, b"")

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
                    break # No rompemos ya que sabemos que llego toda la informacion
                pass

        self.skt.settimeout(None)  



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


  print(f"[ {filled_bar}{empty_bar} ] {completion}", end="\r ")
  if (percentage == 1):
      print("\n")

def calculate_window_size(cantPaquetesAenviar):
    value = cantPaquetesAenviar * lib.constants.WINDOWCONSTANT
    value = math.floor(value)
    print(f"Calculated value: {value}")
    if value < lib.constants.WINDOWTHRESHOLD:
        return math.ceil(cantPaquetesAenviar / 2) 
    return value


