import sys
import socket
# import struct
import os

import lib.SocketRDT 
print(os.getcwd())


#    DIR.archivo
from lib.SocketRDT import SocketRDT, bytesAstr, uint32Aint
import lib.ProtocoloFS
import lib.constants
import threading


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

SERVER_PATH = "data/server/"



seguir_corriendo = True
lock = threading.Lock()


def input_server():
    global seguir_corriendo
    res = input("Presione q para cerrar el servidor")
    if res == "q":
        with lock:
            seguir_corriendo = False

        print("Cerrando servidor...")

class Listener:
        def __init__ (self, ip, port):
            self.recieveSocket = SocketRDT(lib.constants.TIPODEPROTOCOLO, None,
                                        (0,0), ip, port)

        def listen(self):
            # TODO: Poner en un loop y hacer que esto sea multithread
            # Cada worker deberia estar en su propio thread
            paquete, addr  = self.recieveSocket.acceptConnection()


            self.handshake(addr, UDP_IP, paquete)
            # worker(addr, UDP_IP)
            # w = Worker(addr, UDP_IP)
            # w.hablar()

        def handshake(self, addressCliente, myIP, paquete):
            socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, paquete.tipo, addressCliente, myIP)
            nuevoPuerto = socketRDT.skt.getsockname()[1]
            self.recieveSocket.syncAck(nuevoPuerto, socketRDT, paquete)

            worker(socketRDT, paquete)


def worker(socketRDT, paquete):
    # socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, addressCliente, myIP)
    # socketRDT.syncAck()
    # addressCliente = socketRDT.skt.getpeername() 
    addressCliente = socketRDT.peerAddr
    nombre = bytesAstr(paquete.getPayload())
    tipo = paquete.tipo
    # Con esto vemos si es upload (UPL) o Download (DOW)
    # Por ahora que solo estamos implementando upload no lo usamos
    
    # pathArchivo = nombre[len(lib.constants.MENSAJEUPLOAD):]
    # pathArchivo = bytesAstr(pathArchivo)

    if tipo == lib.constants.UPLOAD:

        nombreArchivo = nombre.split("/")[-1]
    
        # TODO: No me capta el tipo correctamente. Arreglar
        # if tipo == lib.constants.MENSAJEUPLOAD:
        #archivo_recibido = lib.ProtocoloFS.recibirArchivo(socketRDT, pathArchivo)
        
        # print(f"\033[93mRecibiendo '{nombreArchivo}' de {addressCliente}...\033[0m")
        archivo_recibido = socketRDT.receive_all()
    
        print("\033[92mArchivo Recibido!\033[0m")


        with open(SERVER_PATH + nombreArchivo, "wb") as file:
            file.write(archivo_recibido)


    elif tipo == lib.constants.DOWNLOAD:
        socketRDT.sendall("ack".encode())

        try: 
            print(f"\033[93mEnviando '{nombre}' a {addressCliente}...\033[0m")
            
            with open(nombre, "rb") as file:
                archivo = file.read()
            
                socketRDT.sendall(archivo)
                
        except FileNotFoundError:
            print(f"El archivo {nombre} no existe")
            


    

# class Worker:
#     def __init__ (self, addressCliente, myIP):
#         self.socketRDT = SocketRDT(lib.constants.TIPODEPROTOCOLO, addressCliente, myIP)

#         self.socketRDT.syncAck()

#         self.socketRDT.receive_all(mensaje)

#         if mensaje == "voy a subir":
#             upload()
#         else:
#             download()


#         print(f"Creo un worker con Puerto: {self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA]}")
        
#     def hablar(self):
#         data = self.socketRDT.receive_all()
#         print ("\033[94mEl worker recibió: ", data.decode('utf-8'), " de: ", self.socketRDT.peerAddr[lib.constants.PUERTOTUPLA], "\n \033[0")

#         message = data.upper()
#         message_bytes = bytes(f"{message}", 'utf-8')

#         self.socketRDT.sendall(message_bytes)
    
    


def __main__():
    if lib.constants.TIPODEPROTOCOLO != "SW" and lib.constants.TIPODEPROTOCOLO != "SR":
        sys.exit(f'''
\033[91mERROR\033[0m: Tipo de protocolo desconocido: {lib.constants.TIPODEPROTOCOLO}''')

    l = Listener(UDP_IP, UDP_PORT)
    l.listen()

__main__()
