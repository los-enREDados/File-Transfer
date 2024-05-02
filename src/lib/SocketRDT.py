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
        

    def syncAck(self):
        # Este mensaje podria ser mas corto o no estar directamente
        # Solo necesitamos mandarle esto para que reciba la direccion
        mensaje = lib.constants.MENSAJEACEPTARCONECCION

        self.skt.sendto(mensaje, self.peerAddr)


    def connect(self):
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)
        synAck = b""
        addr = 0

        while synAck != lib.constants.MENSAJEACEPTARCONECCION:
           
            try: 
                print("Enviando SYN a ", self.peerAddr)
                self.skt.sendto(lib.constants.MENSAJECONECCION, self.peerAddr)
                synAck, addr = self.skt.recvfrom(len(lib.constants.MENSAJEACEPTARCONECCION)) 
                if addr[0] != self.peerAddr[0]:
                    print("Contesto otro server")
                    raise ValueError("Se conecto a otro servidor")

            except TimeoutError:
                # Volver a ejecutar
                print("TIMEOUT")
                pass
          
        self.skt.settimeout(None)
        self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], addr[lib.constants.PUERTOTUPLA])


        return


    # def connect(self):
    #     # ATTENTION: ¿La forma de conectarse es la misma entre stop and
    #     # wait y selective repeat?
    #     # ATTENTION: el "b" antes del string indica que son bytes
    #     mensaje = lib.constants.MENSAJECONECCION

    #     self.skt.sendto(mensaje, self.peerAddr)
        
    #     # ATTENTION: Lo importante, es el addres. Esta tiene el puerto
    #     # con el que voy a hablar
    #     synAck = b""
    #     while synAck != lib.constants.MENSAJEACEPTARCONECCION:
    #         # No me interesa lo que me manden HASTA QUE alguien me
    #         # mande un SYNACK
    #         synAck, addr = self.skt.recvfrom(len(lib.constants.MENSAJEACEPTARCONECCION)) # buffer size is 1024 bytes

    #     # Actualizo el peer addres, poniendo ahora el puerto nuevo
    #     self.peerAddr = (self.peerAddr[lib.constants.IPTUPLA], addr[lib.constants.PUERTOTUPLA])

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

    # def _send_stop_and_wait(self,)

    def _pkt_sent_ok(self, ack_pkt: bytes, seqNum: int):
        # Aclaracion: El ACK es directamente el numero de 
        # paquete recibido por el otro
        seqNumRecibido = uint32Aint(ack_pkt)

        return seqNumRecibido == seqNum

    def _sendall_stop_and_wait(self, mensaje: bytes):
        self.skt.settimeout(lib.constants.TIMEOUTSENDER)

        # print("\033[92m")
        # print("==================INICIO SENDALL==================")
        # print("\033[0m")
        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAQUETE
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)
        # Header:
        # Sequence number
        # Fin
        
        #test = False
        #print(f"mensaje: {mensaje}")
        print(f"cantPaquetesAenviar: {cantPaquetesAenviar}")

        seqNum = 0
        while seqNum <= cantPaquetesAenviar:
            #print(f"************PAQUETE SEQNUM: {seqNum}************")
           
            try: 
                #------------------------------------------------------------------------------------------------------------------------\
                #     ___                                                                                          _                    #|
                #    / _ \                                                                                        | |                   #|
                #   / /_\ \_ __ _ __ ___   __ _ _ __ ___   ___  ___    _   _ _ __     _ __   __ _  __ _ _   _  ___| |_ ___              #|
                #   |  _  | '__| '_ ` _ \ / _` | '_ ` _ \ / _ \/ __|  | | | | '_ \   | '_ \ / _` |/ _` | | | |/ _ \ __/ _ \             #|
                #   | | | | |  | | | | | | (_| | | | | | | (_) \__ \  | |_| | | | |  | |_) | (_| | (_| | |_| |  __/ ||  __/             #|
                #   \_| |_/_|  |_| |_| |_|\__,_|_| |_| |_|\___/|___/   \__,_|_| |_|  | .__/ \__,_|\__, |\__,_|\___|\__\___|             #|
                #                                                                    | |             | |                                #|
                #                                                                    |_|             |_|                                #|
                                                                                                                                        #|
                                                                                                                                        #|                
                indiceInicial = seqNum * lib.constants.TAMANOPAQUETE                                                                    #|
                indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1     #|           
                                                                                                                                        #|
                payloadActual = mensaje[indiceInicial:indiceFinal]                                                                      #|
                                                                                                                                        #|
                                                                                                                                        #|
                                                                                                                                        #|
                if seqNum == cantPaquetesAenviar:                                                                                       #|
                    paquete = Paquete(seqNum, lib.constants.FIN, payloadActual)                                                         #|
                else:                                                                                                                   #|
                    paquete = Paquete(seqNum, lib.constants.NOFIN, payloadActual)                                                       #|
                                                                                                                                        #|
                                                                                                                                        #|
                                                                                                                                        #|
                                                                                                                                        #|
                # ----------------------------------------------------------------------------------------------------------------------/
                
                # Enviamos el paquete
                # print("+-----enviando paquete:------+")
                # print(f"|  seqNum: {seqNum}")
                # print(f"|  fin: {paquete.fin}")
                # print(f"|  payload: {payloadActual}")
                # print(f"+-----------------------------+")

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
            
                # numPaqueteRecibo, _ = self.skt.recvfrom(lib.constants.TAMANOHEADER)
                # numPaqueteRecibo = uint32Aint(numPaqueteRecibo)
                
                # if numPaqueteRecibo != numPaquete:
                #     # Yo le queria enviar un numero distinto; pero
                #     # me dijo que estaba esperando un numero distinto
                #     # en ese caso, tengo que enviarle lo que el espera
                #     # esto deberia ser SIEMPRE? el numero anterior
                #     # por como funciona el stop and wait
                #     numPaquete = numPaqueteRecibo
                #     if numPaquete == cantPaquetesAenviar:
                #         break

                #     raise IndexError

                # # Cada paquete es: primeros 4 bytes para el secuence numbers
                # # siguientes es data
                # indiceInicial = numPaquete*lib.constants.TAMANOPAQUETE
                # indiceFinal = (numPaquete + 1) *lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1 
                # print(f"Numero paquete: {numPaquete}")

                # payloadActual = mensaje[indiceInicial:indiceFinal]
                # paquete = Paquete(numPaquete, payloadActual)

                # # WARNING: Este codigo existe solo para dropear un paquete
                # # articifialmente. Lo mismo la variable test
                # if not(numPaquete == 2 and test == True):
                #     self.skt.sendto(paquete.misBytes, self.peerAddr)
                # else:
                #     test = False
                #     print("Pierdo un paquete a proposito")


                # numPaquete += 1

  
        self.skt.settimeout(None)
    
        # sys.exit("\033[91mDE ACA EN ADELANTE, NO ESTA IMPLEMENTADO\033[0m")

        # pass
        # print("\033[92m")
        # print("==================TERMINO SENDALL==================")
        # print("\033[0m")
        return
    

    def _receive_stop_and_wait(self,):
        # Esto me va a devolver un addr y data.
        # addr yo "en teoria" ya lo conozco
        # data es lo importante. TODO: Chequear misma direccion
        
        # cantPaquetes, _ = self._recieve(lib.constants.TAMANOHEADER)
        # cantPaquetes = uint32Aint(cantPaquetes)

        # self.skt.sendto(lib.constants.MENSAJEACK, self.peerAddr)
        
        # self.skt.settimeout(lib.constants.TIMEOUT);
        # print("\033[93m")
        # print("==================INICIO RECEIVEALL==================")
        # print("\033[0m")


        
        mensajeFinal = bytearray()

        es_fin = False
        ultimoSeqNumACK = -1
        while not es_fin:

            #print(f"*******PAQUETE SEQNUM QUE ESPERO: {ultimoSeqNumACK + 1}*******")

            # Recibo paquete
            bytes_paquete = self._recieve(lib.constants.TAMANOPAQUETE + lib.constants.TAMANOHEADER)
       
            paquete = Paquete.Paquete_from_bytes(bytes_paquete)
            # print("+-----paquete recibido:------+")
            # print(f"|  seqNum: {paquete.getSequenceNumber()}")
            # print(f"|  fin: {paquete.fin}")
            # print(f"|  payload: {paquete.payload}")
            # print(f"+-----------------------------+")

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
        
        # empiezo a contar
        # recibo por las dudas
        # mando ack
        #


        # test = False

        # seqNum = 0
        # while seqNum <= cantPaquetes:
        #     pass
            #
            # try:

                # # ATTENTION: Puede parecer extrano que el reciever le
                # # mande el sequence number primero al sender.
                # # Es medio raro.
                # # Esta fue la mejor solucion que se me ocurrio al
                # # problema de "Que pasa si EL SENDER" tiene timeout
                # numPaqueteActualUint = intAUint32(seqNum)
                # self.skt.sendto(numPaqueteActualUint, self.peerAddr)

                # # WARNING: Este codigo existe solo para dropear un paquete
                # # articifialmente. Lo mismo la variable test
                # if seqNum == 3 and test == True:
                #     print("Pierdo paquete")
                #     test = False
                #     continue

                # data, _ = self.skt.recvfrom(lib.constants.TAMANOPAQUETE) # buffer size is 1024 bytes

                # seqNum = uint32Aint(data[0:lib.constants.TAMANOHEADER])
                # seqNum += 1

                # message = data[lib.constants.TAMANOHEADER + 1:]

                # mensajeFinal.extend(message)
                # print(seqNum)
                # print(message)

                # print(f"seq {seqNum}")
                # print(f"cant {cantPaquetes}")

                # numPaquete += 1
            # except TimeoutError:
            #     # Volver a ejecutar
            #     print("TIMEOUT")
            #     pass

        # Lo ponemos de vuelta en modo bloqueante:
        # Fuente: https://docs.python.org/3/library/socket.html#socket.socket.settimeout
        # self.skt.settimeout(None)

        # sys.exit("\033[91mDE ACA EN ADELANTE, NO ESTA IMPLEMENTADO\033[0m")

        # print("\033[93m")
        # print("==================TERMINO RECEIVEALL==================")
        # print("\033[0m")
        return mensajeFinal

    def _chequear_timeouts(self, lista_de_timeouts, tiempo_ahora):
        lista_de_timeouts_actualizada = lista_de_timeouts
        indice_seq_number_perdido = -1

        for i in range(len(lista_de_timeouts_actualizada)):
            celda = lista_de_timeouts_actualizada[i]
            seq_number = celda[0]
            tiempo_de_envio = celda[1]
            # Si todavia no tiene envio, no hago nada
            if tiempo_de_envio == None:
                continue

            segundos_sin_ack = (tiempo_de_envio - tiempo_ahora).total_seconds()

            # Apenas encuentro uno, lo quiero reenviar
            if segundos_sin_ack > lib.constants.TIEMOUTPORPAQUETESR:
                indice_seq_number_perdido = i
                break

        seq_number_perdido = -1 # -1 significa que no hubo timeout
                
        # No lo saco por miedo a sacar algo en el medio de un for
        if indice_seq_number_perdido != -1:
            seq_number_perdido = lista_de_timeouts_actualizada[indice_seq_number_perdido][0]

            # NOTE: Lo saco de la lista de timeouts porque "ya no aplica ese timeout".
            # Cuando envie de nuevo el paquete perdido, voy a volver a actualizar la lista
            lista_de_timeouts_actualizada[indice_seq_number_perdido] = (None, None, False)
            
        return seq_number_perdido, lista_de_timeouts_actualizada

    def _obtener_primer_paquete_no_ack(self, listaDeTimeouts, window):
        seqNum = -1
        for i in range(len(listaDeTimeouts)):
#         seqNum = -1 #-1 significa que termine de enviar :D !
#         for i in range(window[0], window[1]+1):
#             if i > window[1]:
#                 print(f'SUCEDIO ALGO. i = " + str(i) + " window[1] = " + str(window[1])', i, window[1])
#                 pass
#                 #sys.exit("EL PRIMERO LIBRE ESTA POR FUERA DE LA WINDOW")
# # [True, False, True, False, False, False, False, False, False, False]
            boolActual = listaDeTimeouts[i][3]
            if boolActual == False:
                seqNum = i
                print(f"Recibi el ack de secuencia: {seqNum}")
                break

        return seqNum

    def _enviar_paquete_SR(self, mensaje: bytes, seqNum: int, list_de_timeouts, cantPaquetesAenviar:int):
        # Busco el primer slot libre, voy a actualizar la lista de timeouts
        indiceEspacioVacio = -1
        for i in range(len(lista_de_timeoutes_actualizada)):
            espacioActual = lista_de_timeoutes_actualizada[i]
            if espacioActual[1] == None:
                indiceEspacioVacio = i
                break


        if indiceEspacioVacio == -1:
            pudeEnviar = False
            return list_de_timeouts, pudeEnviar 
            sys.exit("NO HABIA ESPACIO EN LA VENTANA")


        # NOTE: Si llegue hasta significa que hay espacio en la ventana

        indiceInicial = seqNum * lib.constants.TAMANOPAQUETE
        indiceFinal = (seqNum + 1) * lib.constants.TAMANOPAQUETE #ATTENTION: Ese es no inclusivo, va hasta indice final - 1
        payloadActual = mensaje[indiceInicial:indiceFinal]

        if seqNum == cantPaquetesAenviar:                                                                                       #|
            paquete = Paquete(seqNum, lib.constants.FIN, payloadActual)                                                         #|
        else:                                                                                                                   #|
            paquete = Paquete(seqNum, lib.constants.NOFIN, payloadActual)

        self.skt.sendto(paquete.misBytes, self.peerAddr)

        lista_de_timeoutes_actualizada = list_de_timeouts



        tiempoActual =  datetime.datetime.now()
        lista_de_timeoutes_actualizada[indiceEspacioVacio] = (seqNum, tiempoActual)

        pudeEnviar = True
        return lista_de_timeoutes_actualizada, pudeEnviar


    def _is_ventana_full(self, ventana):
        return
    
    def _actualiza_acks_sr(self, listaDeTimeouts, seqNumRecibido):
        lista_de_timeoutes_actualizada = listaDeTimeouts

        for i in range(len(lista_de_timeoutes_actualizada)):
            celda = lista_de_timeoutes_actualizada[i]
            seqNum = celda[0]
            if seqNum == seqNumRecibido:
                lista_de_timeoutes_actualizada[i][3] = True

        return lista_de_timeoutes_actualizada

# [0, 1, 2, 3, 4]
# [0,2]

# PaqueteActual = ventana[0]
# if PaqueteActual <= ventana[fin]:
    #mandar paquete
    #PaqueteActual += 1


# [0, 1, 2, 3, 4]
        pass  

# Paquete
# - payload
# - Timetout
# - ACK     

    def _sendall_selective(self, mensaje: bytes):

        cantPaquetesAenviar = len(mensaje) / lib.constants.TAMANOPAQUETE
        cantPaquetesAenviar = math.ceil(cantPaquetesAenviar)


        # ATTENTION: Chequear si realmente es // 2
        tamanoVentana = cantPaquetesAenviar // 2

        # ATTENTION: La ventana es una lista de dos valores. Siendo el
        # inicio inclusive y el fin inclusive
        ventana = [0, tamanoVentana]

        # NOTE: Lista de timeouts es una lista de tuplas que representa
        # (Sequence number, tiempo de envio [clase datetime de Python])
        # La inicializo "con valores default"
        # listadeTimeous = [(seqNum, tiempoDeEnvio), ...]
        listaDeTimeouts = [(None, None, False)] * tamanoVentana 
        

        #listaDeACKS     = [False] * cantPaquetesAenviar
        #listaDeACKS     = [False] * tamanoVentana


        sequenceMasChicoSinACK = 0
        seqNumAEnviar = 0
        seqNumActual = 0 

        self.skt.settimeout(lib.constants.TIMEOUTSENDERSR)

        while sequenceMasChicoSinACK != -1:
# [0, 1, 2, 3, 4]
# [0, 2]
# [(None, None), (None, None), (None, None), (None, None), (None, None)]

# 1: [(0, T0), (None, None), (None, None), (None, None), (None, None)]
# 2: [(0, T0), (1, T1), (None, None), (None, None), (None, None)]
# 3: [(0, T0), (1, T1), (2, T2), (None, None), (None, None)]


            try:
                tiempoActual =  datetime.datetime.now()

                seqNumPerdido, listaDeTimeouts = self._chequear_timeouts_(listaDeTimeouts, tiempoActual)

                if seqNumPerdido != -1:
                    seqNumAEnviar = seqNumPerdido
                    
                else:
                    seqNumAEnviar = seqNumActual
                #    seqNumActual = self._obtener_primer_paquete_no_ack(listaDeACKS, sequenceMasChicoSinACK, ventana)
                    if seqNumAEnviar < ventana[1] :
                        seqNumActual += 1
    
    
                listaDeTimeouts, pudeEnviar = self._enviar_paquete_SR(mensaje, seqNumAEnviar, listaDeTimeouts, cantPaquetesAenviar)
                
                # NOTE: No va a poder enviar cuando la ventana este llena
                if pudeEnviar == True:
                    continue

                ack_pkt = self._recieve(lib.constants.TAMANONUMERORED)

                
                seqNumRecibidio = uint32Aint(ack_pkt)

                
                listaDeTimeouts = self._actualiza_acks_sr(listaDeTimeouts, seqNumRecibido)

                if seqNumRecibidio == ventana[0]:
                    nuevoComienzoVentana = self._obtener_primer_paquete_no_ack(listaDeTimeouts, ventana)
                    ventana = [nuevoComienzoVentana, nuevoComienzoVentana + tamanoVentana]
            
            except TimeoutError:
                print("TIMEOUT")
                pass

        self.skt.settimeout(None)  

        # sys.exit("NO IMPLEMENTADO")
        pass


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
        while True:
            if seq_num_de_fin and cant_recibidos == seq_num_de_fin+1:
                break
       
            bytes_paquete = self._recieve(lib.constants.TAMANOPAQUETE + lib.constants.TAMANOHEADER)

            paquete = Paquete.Paquete_from_bytes(bytes_paquete)

            seqNumRecibido = paquete.getSequenceNumber() #5

            self.skt.sendto(intAUint32(seqNumRecibido), self.peerAddr)

            payload = paquete.getPayload()

            
            mensajeFinal[seqNumRecibido] = payload

            if paquete.fin:
                seq_num_de_fin = paquete.seqNum

            cant_recibidos += 1

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
